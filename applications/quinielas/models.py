from django.conf import settings
from applications.users.models import User
from django.db import models
from model_utils.models import TimeStampedModel
from django.db.models.signals import post_save

class Equipos(models.Model):
    # Model Equipos
    nombre = models.CharField("Nombre", max_length=200, unique=True)
    logo = models.CharField("Logo", max_length=600, blank=True, null=True)
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"

    def __str__(self):
        return str(self.nombre)

class Partidos(TimeStampedModel):
    # Model Partidos
    local = models.ForeignKey(Equipos, on_delete=models.CASCADE, related_name='local_equipos')
    visitante = models.ForeignKey(Equipos, on_delete=models.CASCADE, related_name='visitantes_equipos')
    fecha_hora = models.DateTimeField("Fecha y Hora")
    resultado_local = models.IntegerField("Resultado Local", default=0)
    resultado_visitante = models.IntegerField("Resultado Visitante", default=0)
    ganador = models.IntegerField("Ganador", default=0)

    class Meta:
        verbose_name = "Partido"
        verbose_name_plural = "Partidos"

    def save(self, *args, **kwargs):
        if self.resultado_local > self.resultado_visitante:
            # LOCAL
            self.ganador = 1
        elif self.resultado_local < self.resultado_visitante:
            # VISITANTE
            self.ganador = 2
        elif self.resultado_local == self.resultado_visitante:
            # EMPATE
            self.ganador = 3
        
        super(Partidos, self).save(*args, **kwargs)

    def __str__(self):
        return "%s vs %s" % (self.local.nombre.upper(), self.visitante.nombre.upper())

class Pronostico(TimeStampedModel):
    # Model Pronósticos
    partido = models.ForeignKey(Partidos, on_delete=models.CASCADE, related_name='pronostico_partido')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usuario_user')
    pronostico = models.IntegerField('Pronóstico', default=0)
    puntos = models.IntegerField('Puntos', default=0)
    pronostico_local = models.IntegerField("Resultado Local", default=0)
    pronostico_visitante = models.IntegerField("Resultado Visitante", default=0)

    class Meta:
        verbose_name = "Pronostico"
        verbose_name_plural = "Pronosticos"
    
    def pronostico_usuario(self):
        if self.pronostico == 1:
            pronostico = 'Gana %s (local)' % self.partido.local.nombre
        elif self.pronostico == 2:
            pronostico = 'Gana %s (visitante)' % self.partido.visitante.nombre
        elif self.pronostico == 3:
            pronostico = 'Empate'
        else:
            pronostico = '-'

        return pronostico
    
    def resultado_partido(self):
        if self.partido.ganador == 1:
            resultado = 'Ganó %s (local)' % self.partido.local.nombre
        elif self.partido.ganador == 2:
            resultado = 'Ganó %s (visitante)' % self.partido.visitante.nombre
        elif self.partido.ganador == 3:
            resultado = 'Empate'
        else:
            resultado = '-'

        return resultado

    def puntos_x_partido(self):
        total = 0
        if self.pronostico == self.partido.ganador:
            total += 1
        if self.pronostico_local == self.partido.resultado_local and self.pronostico_visitante == self.partido.resultado_visitante:
            total += 1

        return total

    def save(self, *args, **kwargs):
        if self.pronostico_local > self.pronostico_visitante:
            # LOCAL
            self.pronostico = 1
        elif self.pronostico_local < self.pronostico_visitante:
            # VISITANTE
            self.pronostico = 2
        elif self.pronostico_local == self.pronostico_visitante:
            # EMPATE
            self.pronostico = 3
        
        super(Pronostico, self).save(*args, **kwargs)

    def __str__(self):
        return "%s partido: %s vs %s" % (self.usuario, self.partido.local.nombre.upper(), self.partido.visitante.nombre.upper())


# Se ejecutara cada que se capturen resultados por cada partido.
def actualizar_puntos(sender, instance, created, **kwargs):
    if not created:
        resultado_local = instance.resultado_local
        resultado_visitante = instance.resultado_visitante
        ganador = instance.ganador

        # Filtramos todos los partidos del pronostico
        queryset = Pronostico.objects.filter(
            partido=instance.pk
        )

        for row in queryset:
            puntos = 0
            if row.pronostico_local == resultado_local and row.pronostico_visitante == resultado_visitante:
                # PUNTO POR ATINARLE AL RESULTADO EN GOLES
                puntos += 1
            if row.pronostico == ganador:
                # PUNTO POR ATINARLE AL RESULTADO (LOCAL, VISTANTE, EMPATE)
                puntos += 1
            row.puntos = puntos
            row.save()


post_save.connect(actualizar_puntos, sender=Partidos)