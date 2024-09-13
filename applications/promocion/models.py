from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from django.db.models.signals import post_save

from .managers import (EventoManager, FormularioManager, VisitaDetalleManager,
                       VisitaManager)


class Programa_Actualizaciones(TimeStampedModel):
    """ Model Programa Actualizaciones """

    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.CharField('Descripcion', max_length=400, blank=True)
    objetivo = models.CharField('Objetivo', max_length=400, blank=True,  null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Programa Actualizaciones'
        verbose_name_plural = 'Programa Actualizaciones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Detalle(models.Model):
    """ Model Detalle """

    programa = models.ForeignKey(Programa_Actualizaciones, on_delete=models.CASCADE, related_name='detalle_programa')
    fecha = models.DateField('Fecha', blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=600, blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalle'
        ordering = ['programa']

    def __str__(self):
        return str(self.programa)


class Evento(TimeStampedModel):
    """ Model Evento """

    nombre = models.CharField('Nombre', max_length=200)
    id_programa = models.ForeignKey(
        Programa_Actualizaciones, on_delete=models.CASCADE, related_name='evento_programa')
    descripcion = models.CharField(
        'Descripcion', max_length=400, blank=True)
    direccion = models.CharField(
        'Direccion', max_length=400, blank=True)
    ciudad = models.CharField(
        'Ciudad', max_length=200, blank=True)
    tipo = models.CharField('Estatus', max_length=100, blank=True, null=True)
    unidades_censadas = models.CharField('Unidades Censadas', max_length=100, blank=True, null=True)
    km2_recorridos = models.CharField('Km2 Recorridos', max_length=100, blank=True, null=True)

    objects = EventoManager()

    class Meta:
        verbose_name = 'Eventos'
        verbose_name_plural = 'Eventos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return self.nombre + ' ' + self.ciudad


class Desarrollo(TimeStampedModel):
    """ Model Desarrollo """

    id_evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name='desarrollo_evento')
    fecha_inicio = models.DateField('Fecha Inicio', blank=True)
    fecha_fin = models.DateField('Fecha Fin', blank=True)
    fecha_inicio_campo = models.DateField('Fecha Inicio Campo', blank=True, null=True)
    fecha_fin_campo = models.DateField('Fecha Fin Campo', blank=True, null=True)
    fecha_inicio_calidad = models.DateField('Fecha Inicio Calidad', blank=True, null=True)
    fecha_fin_calidad = models.DateField('Fecha Fin Calidad', blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    responsables = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='responsables', blank=True
    )
    jefatura = models.CharField('Jefatura', max_length=100, blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=600, blank=True, null=True)

    class Meta:
        verbose_name = 'Desarrollo'
        verbose_name_plural = 'Desarrollo'
        ordering = ['id_evento', 'fecha_inicio']
        indexes = [
            models.Index(fields=['id']),
        ]

    def __str__(self):
        return str(self.id_evento) + " (" + str(self.fecha_inicio) + '--' + str(self.fecha_fin) + ")"


class Participantes(TimeStampedModel):
    """ Model Participantes """

    id_usuario = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='usuarios_participantes')
    id_desarrollo = models.ForeignKey(
        Desarrollo, on_delete=models.CASCADE, related_name='desarrollo_usuarios')
    fecha_inicio = models.DateField('Fecha Inicio', blank=True)
    fecha_fin = models.DateField('Fecha Fin', blank=True)

    class Meta:
        verbose_name = 'Participantes'
        verbose_name_plural = 'Participantes'
        ordering = ['id_desarrollo', 'fecha_inicio']

    def __str__(self):
        return str(self.id_desarrollo)


class Actividades(TimeStampedModel):  # cambiar
    """ Model Actividades """

    actividad = models.CharField('Actividad', max_length=200)
    tipo_tramite = models.CharField('Tipo Tramite', max_length=200, blank=True)
    descripcion = models.CharField('Descripcion', max_length=400, blank=True)

    class Meta:
        verbose_name = 'Actividades'
        verbose_name_plural = 'Actividades'
        ordering = ['actividad']
        indexes = [
            models.Index(fields=['actividad']),
        ]

    def __str__(self):
        return self.actividad + ' ' + self.tipo_tramite


class Formulario(models.Model):
    """ Model Formulario """

    id_actividad = models.ForeignKey(
        Actividades, on_delete=models.CASCADE, related_name='formulario_actividad')
    etiqueta = models.CharField('Etiqueta', max_length=254)
    campo = models.CharField('Campo', max_length=254)
    tipo_control = models.CharField('Tipo Control', max_length=254)
    is_visible = models.BooleanField('Visible', default=True)
    is_required = models.BooleanField('Requerido', default=True)
    consulta = models.CharField(
        'Consulta', max_length=500, blank=True, null=True)

    objects = FormularioManager()

    class Meta:
        verbose_name = 'Formularios'
        verbose_name_plural = 'Formularios'
        ordering = ['id_actividad']

    def __str__(self):
        return str(self.id_actividad) + ' (' + self.etiqueta + ')'


class Visita(TimeStampedModel):
    """ Model Visita """

    id_desarrollo = models.ForeignKey(
        Desarrollo, on_delete=models.CASCADE, related_name='visita_desarrollo')
    usuario = models.CharField('Usuario', max_length=100)
    rfc = models.CharField('RFC', max_length=20)
    nombre = models.CharField('Nombre', max_length=254)
    fecha = models.DateField('Fecha', blank=True)
    is_active = models.BooleanField('Activo', default=True)

    objects = VisitaManager()

    class Meta:
        verbose_name = 'Visita'
        verbose_name_plural = 'Visita'
        ordering = ['id_desarrollo', 'rfc']
        indexes = [
            models.Index(fields=['id']),
        ]

    def __str__(self):
        return self.rfc


class Visita_Detalle(TimeStampedModel):
    """ Model Vista_Detalle """

    folio = models.PositiveIntegerField('Folio', blank=True)
    id_visita = models.ForeignKey(
        Visita, on_delete=models.CASCADE, related_name='detalle_visita')
    id_actividad = models.ForeignKey(
        Actividades, on_delete=models.CASCADE, related_name='detalle_actividad')
    dato = models.CharField('Datos', max_length=254, blank=True)
    valor = models.CharField('Valor', max_length=500, blank=True)
    usuario = models.CharField('Usuario', max_length=100, blank=True)

    objects = VisitaDetalleManager()

    class Meta:
        verbose_name = 'Detalle visita'
        verbose_name_plural = 'Detalle visita'
        ordering = ['id_visita']

    def __str__(self):
        return str(self.folio)


class Opciones(models.Model):
    """ Model Opciones """

    codigo = models.CharField('Codigo', max_length=100, blank=False)
    valor = models.CharField('Valor', max_length=200, blank=True)
    comentario = models.CharField('Comentario', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Opciones'
        verbose_name_plural = 'Opciones'
        ordering = ['codigo']

    def __str__(self):
        return self.comentario


def insert_detail(sender, instance, created, **kwargs):
    if created:
        detail = Detalle(
            programa=instance,
            fecha=instance.created,
            comentarios='',
            estatus='NUEVO',
            usuario=instance.usuario
        )
        detail.save()


post_save.connect(insert_detail, sender=Programa_Actualizaciones)

