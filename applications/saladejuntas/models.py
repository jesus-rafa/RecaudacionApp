from django.conf import settings
from django.db import models
from applications.users.models import User, Areas
from model_utils.models import TimeStampedModel


class Categoria(TimeStampedModel):
    descripcion = models.CharField("Descripción", max_length=255)
    color = models.CharField("Color", max_length=255)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    
    def __str__(self):
        return str(self.descripcion)


class Sala(TimeStampedModel):
    descripcion = models.CharField("Nombre", max_length=255)
    detalle_descripcion = models.CharField("Descripción", max_length=500, null=True, blank=True)
    capacidad_sala = models.IntegerField("Número máximo de personas")
    calendario_id = models.CharField("Calendario id", max_length=500, null=True, blank=True)
    color = models.CharField("Color", max_length=255, null=True, blank=True)
    color_name = models.CharField("Etiqueta Color", max_length=255, null=True, blank=True)
    ordenamiento = models.IntegerField("Ordenar",default=1,null=True)
    is_active = models.BooleanField("Registro Activo", default=True)

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
    
    def __str__(self):
        return str(self.descripcion)


class EstatusReuniones(TimeStampedModel):
    descripcion = models.CharField("Descripcion", max_length=255)

    class Meta:
        verbose_name = "Estatus Reuniones"
        verbose_name_plural = "Estatus Reuniones"
    
    def __str__(self):
        return str(self.descripcion)


class notificacionesCoffeBreak(TimeStampedModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_notificaciones_coffe_break")
    nombre = models.CharField("Nombre", max_length=500, null=True, blank=True)
    correo = models.CharField("Correo", max_length=500, null=True, blank=True)
    is_active = models.BooleanField("Registro Activo", default=True)

    class Meta:
        verbose_name = "Notificación Coffe Break"
        verbose_name_plural = "Notificaciones Coffe Break"
    
    def __str__(self):
        return str(self.nombre)


class Reuniones(models.Model):
    evento_id = models.CharField("Evento", max_length=500, null=True, blank=True)
    descripcion_evento = models.CharField("Descripción Evento", max_length=500, null=True, blank=True)
    evento = models.CharField("Evento", max_length=255, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name = "reunion_sala_de_juntas")
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name = "sala_sala_de_juntas")
    area = models.ForeignKey(Areas, on_delete=models.CASCADE, related_name = "area_sala_de_juntas")
    fecha_reunion = models.DateField("Fecha Reunión", auto_now=False, auto_now_add=False) 
    hora_ini_reunion = models.CharField("Hora Inicio", max_length=5)
    hora_fin_reunion = models.CharField("Hora Fin", max_length=5)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_sala_de_juntas")
    usuario_responsable = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_responsable_reunion", null=True, blank=True)
    tiempo = models.IntegerField("Tiempo", default=0)
    is_active = models.BooleanField("Registro Activo", default=True)
    requiere_coffe_break = models.BooleanField("Requiere Coffe Break", default=False)
    tiempo_coffe_break = models.IntegerField("Tiempo Coffe Break", default=0)
    estatus = models.ForeignKey(EstatusReuniones, on_delete=models.CASCADE, related_name = "estatus_sala_de_juntas")
    responsable_reunion = models.CharField("Responsable", max_length=500)
    detalles_coffe_break = models.CharField("Detalles", max_length=500, null=True, blank=True)
    usuario_noti_coffe_break = models.ForeignKey(notificacionesCoffeBreak, on_delete=models.CASCADE, related_name="notificaciones_coffe_break_reuniones", null=True, blank=True)
    total_participantes = models.IntegerField("Total Personas", default=0)

    class Meta:
        verbose_name = "Reunión"
        verbose_name_plural = "Reuniones"
    
    def __str__(self):
        return str(self.evento)
    
    def fecha_hora_inicio_reunion(self):
        return str(self.fecha_reunion) + " " + str(self.hora_ini_reunion) +":00"
    
    def fecha_hora_fin_reunion(self):
        return str(self.fecha_reunion) + " " + str(self.hora_fin_reunion) +":00"


class HistoricoReuniones(TimeStampedModel):
    reunion_sala_de_juntas = models.ForeignKey(Reuniones, on_delete=models.CASCADE, related_name="historico_sala_de_juntas")
    descripcion = models.CharField("Acción", max_length=500)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_historico_sala_de_juntas")
    estatus = models.ForeignKey(EstatusReuniones, on_delete=models.CASCADE, related_name = "hist_estatus_sala_de_juntas")

    class Meta:
        verbose_name = "Histórico Reuniones"
        verbose_name_plural = "Histórico Reuniones"
    
    def __str__(self):
        return str(self.descripcion)


class ParticipantesReuniones(TimeStampedModel):
    reunion_sala_de_juntas = models.ForeignKey(Reuniones, on_delete=models.CASCADE, related_name="participantes_sala_de_juntas")
    correo = models.CharField("Correo Electrónico", max_length=255)
    nombre = models.CharField("Participante", max_length=255)
    is_active = models.BooleanField("Registro Activo", default=True)

    class Meta:
        verbose_name = "Participantes Reuniones"
        verbose_name_plural = "Participantes Reuniones"
    
    def __str__(self):
        return str(self.nombre)
