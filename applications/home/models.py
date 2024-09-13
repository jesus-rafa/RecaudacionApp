from pickle import FALSE
from django.db import models
from model_utils.models import TimeStampedModel


class Codigos_Maestros(models.Model):
    """ Model Codigos Generalizados """

    codigo = models.CharField('Codigo', max_length=100, blank=False)
    valor = models.CharField('Valor', max_length=200, blank=True)
    comentario = models.CharField('Comentario', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Codigos Maestros'
        verbose_name_plural = 'Codigos Maestros'
        ordering = ['codigo']
        

    def __str__(self):
        #return self.codigo + ' ' + self.valor + ' ' + self.comentario
        return self.comentario


class Oficinas(models.Model):
    clave = models.CharField('Clave', max_length=100, unique=True)
    nombre = models.CharField('Nombre', max_length=100, blank=True)
    municipio = models.CharField('Municipio', max_length=100, blank=True)
    is_active = models.BooleanField('is_active', default=True)
    direccion = models.CharField('Direccion', max_length=300, blank=True)

    class Meta:
        verbose_name = 'Oficinas'
        verbose_name_plural = 'Oficinas'
        ordering = ['clave']

    def __str__(self):
        return self.clave


class Dias_Festivos(models.Model):
    """ Model Dias Festivos """

    fecha = models.DateField('Fecha', unique=True)
    comentarios = models.CharField('Comentarios', max_length=400, blank=True, null=True)
    is_general = models.BooleanField('is_general', default=False)
    is_estatal = models.BooleanField('is_estatal', default=False)
    is_federal = models.BooleanField('is_federal', default=False)


    class Meta:
        verbose_name = 'Dias Festivos'
        verbose_name_plural = 'Dias Festivos'
        ordering = ['fecha']
        
    def __str__(self):
        return str(self.fecha) + ' - ' + self.comentarios

class Estado(TimeStampedModel):
    """ Model Estado """

    clave = models.CharField('Clave', max_length=2)
    nombre = models.CharField('Nombre', max_length=40)
    abrev  = models.CharField('Abreviatura', max_length=10)
    activo = models.BooleanField('Estatus', default=True)

    class Meta:
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        ordering = ['id']
        
    def __str__(self):
        return str(self.id)

class Municipio(TimeStampedModel):
    """ Model Municipio """

    estado = models.ForeignKey(
        Estado, on_delete=models.CASCADE, related_name="estado_pertenece"
    )
    clave = models.CharField('Clave', max_length=3)
    nombre = models.CharField('Nombre', max_length=100)
    activo = models.BooleanField('Estatus', default=True)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['id']
        
    def __str__(self):
        return str(self.nombre)

