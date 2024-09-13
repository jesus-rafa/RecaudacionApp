import unidecode

from model_utils.models import TimeStampedModel
from django.db import models
from applications.users.models import User, Areas
from .managers import OficiosManager, RecibidosManager


class Permisos(models.Model):
    """ Model Permisos Asignados"""

    usuario = models.CharField('Acceso', max_length=100, blank=True)
    permisos = models.ManyToManyField(User, blank=True)

    class Meta:
        verbose_name = 'Permisos Asigandos'
        verbose_name_plural = 'Permisos Asignados'
        ordering = ['usuario']

    def __str__(self):
        return self.usuario


class Compartidos(models.Model):
    """ Model Permisos Asignados"""

    usuario = models.CharField('Acceso', max_length=100, blank=True)
    compartidos = models.ManyToManyField(User, blank=True)

    class Meta:
        verbose_name = 'Permisos Compartidos'
        verbose_name_plural = 'Permisos Compartidos'
        ordering = ['usuario']

    def __str__(self):
        return self.usuario


class Oficios(TimeStampedModel):
    """ Model Oficios Invitacion """

    folio = models.CharField('Folio', max_length=50, unique=True)
    nombre = models.CharField('A quien va dirigido', max_length=254, blank=True, null=True)
    puesto = models.CharField('Puesto', max_length=254, blank=True, null=True)
    asunto = models.CharField('Asunto', max_length=254, blank=True, null=True)
    dependencia = models.CharField('Dependencia', max_length=254, blank=True, null=True)
    fecha = models.DateField('Fecha Captura', blank=True, null=True)
    usuario = models.CharField('Create_by',  max_length=100, blank=True, null=True)
    pdf = models.FileField(upload_to='media/correspondencia', blank=True, null=True)
    enviado = models.CharField('Enviado por', max_length=100, blank=True, null=True)
    firma = models.CharField('Firma', max_length=100, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=400, blank=True, null=True)
    copia_a = models.ManyToManyField(
        User,
        blank=True,
        related_name="copia_a",
        through='CC',
    )

    objects = OficiosManager()

    class Meta:
        verbose_name = 'Oficios Invitacion'
        verbose_name_plural = 'Oficios Invitacion'
    
    def save(self, *args, **kwargs):
        if self.pdf.name: 
            self.pdf.name = str(unidecode.unidecode(self.pdf.name))
        super(Oficios, self).save(*args, **kwargs)

    def __str__(self):
        return self.folio


class Recibidos(TimeStampedModel):
    """ Model Oficios Recibidos """

    folio = models.CharField('Folio', max_length=50, blank=True, null=True)
    remitente = models.CharField('Remitente', max_length=254, blank=True, null=True)
    puesto = models.CharField('Puesto', max_length=254, blank=True, null=True)
    asunto = models.CharField('Asunto', max_length=254, blank=True, null=True)
    dependencia = models.CharField('Dependencia', max_length=254, blank=True, null=True)
    fecha = models.DateField('Fecha Recibido', blank=True, null=True)
    fecha_respuesta = models.DateField('Fecha Respuesta', blank=True, null=True)
    fecha_vencimiento = models.DateField('Fecha Vencimiento', blank=True, null=True)
    usuario = models.CharField('Create_by',  max_length=100, blank=True, null=True)
    para = models.CharField('Send_to',  max_length=100, blank=True, null=True)
    pdf = models.FileField(upload_to='media/correspondencia', blank=True, null=True)
    pdf_respuesta = models.FileField(upload_to='media/correspondencia', blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=400, blank=True, null=True)
    firma = models.CharField('Firma', max_length=100, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    area = models.CharField('Area', max_length=254, blank=True, null=True)
    cc_externas = models.CharField('CC Externas', max_length=254, blank=True, null=True)
    unidad = models.ForeignKey(Areas, on_delete=models.CASCADE)
    copiar_a = models.ManyToManyField(
        User,
        blank=True,
        related_name="copiar_a",
        through='CCO',
    )

    objects = RecibidosManager()

    class Meta:
        verbose_name = 'Oficios Recibidos'
        verbose_name_plural = 'Oficios Recibidos'

    def save(self, *args, **kwargs):
        if self.pdf.name:
            self.pdf.name = str(unidecode.unidecode(self.pdf.name))
        if self.pdf_respuesta.name:
            self.pdf_respuesta.name = str(unidecode.unidecode(self.pdf_respuesta.name))
        super(Recibidos, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class CCO(TimeStampedModel):
    oficio = models.ForeignKey(Recibidos, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    declinado = models.BooleanField(default=False)
    visto = models.BooleanField(default=False)
    respuesta = models.BooleanField(default=False)
    observaciones = models.CharField('Observaciones', max_length=400, blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=400, blank=True, null=True)
    archivo = models.FileField(upload_to='media/correspondencia', blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    tipo = models.CharField('Tipo', max_length=50, blank=True, null=True)
    enviado_por = models.CharField('Enviado por',  max_length=100, blank=True, null=True)
    fecha_visto = models.DateTimeField('Fecha Visto', blank=True, null=True)
    fecha_respuesta = models.DateTimeField('Fecha Respuesta', blank=True, null=True)

    class Meta:
        verbose_name = 'Recibidos CC'
        verbose_name_plural = 'Recibidos CC'
        ordering = ['id']
        unique_together = ('oficio', 'user', 'enviado_por',)

    def save(self, *args, **kwargs):
        self.archivo.name = str(unidecode.unidecode(self.archivo.name))
        super(CCO, self).save(*args, **kwargs)


class CC(TimeStampedModel):
    oficio = models.ForeignKey(Oficios, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visto = models.BooleanField(default=False)
    comentarios = models.CharField('Comentarios', max_length=400, blank=True, null=True)

    class Meta:
        verbose_name = 'Oficios CC'
        verbose_name_plural = 'Oficios CC'
        ordering = ['id']
        unique_together = ('oficio', 'user',)


class Archivos_Recibidos(models.Model):
    oficio = models.ForeignKey(Recibidos, on_delete=models.CASCADE)
    archivo = models.FileField(
        blank=True,
        upload_to='media/correspondencia/%Y/%m/%d/',
        verbose_name="archivo"
    )

    def save(self, *args, **kwargs):
        self.archivo.name = str(unidecode.unidecode(self.archivo.name))
        super(Archivos_Recibidos, self).save(*args, **kwargs)


class Archivos_Oficios(models.Model):
    oficio = models.ForeignKey(Oficios, on_delete=models.CASCADE)
    archivo = models.FileField(
        blank=True,
        upload_to='media/correspondencia/%Y/%m/%d/',
        verbose_name="archivo"
    )

    def save(self, *args, **kwargs):
        self.archivo.name = str(unidecode.unidecode(self.archivo.name))
        super(Archivos_Oficios, self).save(*args, **kwargs)
