import unidecode
from datetime import datetime, date

from django.db import models
from django.db.models.signals import post_save
from django.db.models import Q, Sum
from .managers import ProgramaManager
from model_utils.models import TimeStampedModel
from applications.users.models import User


class Envio_Insumos_Programas_Padrones(TimeStampedModel):
    """ Model Envio Insumos Programa Padrones """

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="envio_masivo_insumos_usuario", blank=True, null=True)
    nombre_archivo = models.CharField("Nombre archivo", max_length=255, blank=True, null=True)
    ruta_archivo = models.CharField("Ruta archivo", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Envio de insumos programa padrones'
        verbose_name_plural = 'Envios de insumos programa padrones'

    def __str__(self):
        return self.nombre_archivo


class Programa_Padrones_Temporal(models.Model):
    """ Model Programa Padrones Temporal """

    no_control = models.CharField('No Control', max_length=50, blank=True, null=True)
    folio = models.CharField('Folio', max_length=50, blank=True, null=True)
    rfc = models.CharField('RFC', max_length=30, blank=True, null=True)
    programa = models.CharField('Programa', max_length=50, blank=True, null=True)
    presuntiva = models.DecimalField('Estimado', decimal_places=2, max_digits=15, blank=True, null=True)
    recaudado = models.DecimalField('Recaudado', decimal_places=2, max_digits=15, blank=True, null=True)
    dias = models.PositiveIntegerField('Dias Trasncurridos', blank=True, null=True, default=0)
    nombre = models.CharField('Nombre', max_length=200, blank=True, null=True)
    direccion = models.CharField('Direccion', max_length=255, blank=True, null=True)
    fecha = models.DateField('Fecha', auto_now_add=True, blank=True, null=True)
    etapa = models.CharField('Etapa', max_length=50, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    seguimiento = models.CharField('Seguimiento',  max_length=100, blank=True, null=True)
    usuario = models.CharField('Usuario', max_length=100, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Registro activo', default=True)

    class Meta:
        verbose_name = 'Programa Padrones temporal'
        verbose_name_plural = 'Programas Padrones temporal'
 
    def __str__(self):
        return str(self.id)


class Programa_Padrones(TimeStampedModel):
    """ Model Programacion """
    
    no_control = models.CharField('No Control', max_length=50, blank=True, null=True)
    folio = models.CharField('Folio', max_length=50, blank=True, null=True)
    rfc = models.CharField('RFC', max_length=30, blank=True)
    programa = models.CharField('Programa', max_length=50, blank=True, null=True)
    presuntiva = models.DecimalField('Estimado', decimal_places=2, max_digits=15, blank=True, null=True)
    recaudado = models.DecimalField('Recaudado', decimal_places=2, max_digits=15, blank=True, null=True)
    dias = models.PositiveIntegerField('Dias Trasncurridos', blank=True, null=True, default=0)
    nombre = models.CharField('Nombre', max_length=200, blank=True, null=True)
    direccion = models.CharField('Direccion', max_length=255, blank=True, null=True)
    fecha = models.DateField('Fecha', blank=True, null=True)
    etapa = models.CharField('Etapa', max_length=50, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    seguimiento = models.CharField('Seguimiento',  max_length=100, blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    envio_insumos_programa_padrones = models.ForeignKey(Envio_Insumos_Programas_Padrones, on_delete=models.CASCADE, related_name="programa_padrones_envio_insumos", blank=True, null=True)
    registro_masivo = models.BooleanField("Registro cargado masivamente", blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True, null=True, blank=True)

    objects = ProgramaManager()

    class Meta:
        verbose_name = 'Padrones'
        verbose_name_plural = 'Padrones'
        ordering = ['id']
        
    def __str__(self):
        #return str(self.id) + '--' + self.rfc + ' ' +  self.nombre + ' ' + self.programa + ' ' + self.estatus
        return str(self.id)


class Detalle_Padrones(models.Model):
    """ Model Detalle """

    programa_id = models.ForeignKey(Programa_Padrones, on_delete=models.CASCADE)
    fecha = models.DateField('Fecha', blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=255, blank=True, null=True)
    etapa = models.CharField('Etapa', max_length=50, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalle'
        ordering = ['programa_id']

    def __str__(self):
        return str(self.programa_id)


class Archivos_Padrones(models.Model):
    """ Model Archivos """

    programa_id = models.ForeignKey(Programa_Padrones, on_delete=models.CASCADE)
    tipo = models.CharField('Tipo', max_length=100, blank=True, null=True)
    fecha = models.DateField('Fecha', blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=255, blank=True, null=True)
    archivo = models.FileField('Archivo', upload_to='media/programacion', blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Archivos'
        verbose_name_plural = 'Archivos'
        ordering = ['programa_id']

    def save(self, *args, **kwargs):
        self.archivo.name = str(unidecode.unidecode(self.archivo.name))

        super(Archivos_Padrones, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.programa_id)


class Pagos_Padrones(models.Model):
    """ Model Pagos """

    PERIODOS = [
        (1, 'ENE'),
        (2, 'FEB'),
        (3, 'MAR'),
        (4, 'ABR'),
        (5, 'MAY'),
        (6, 'JUN'),
        (7, 'JUL'),
        (8, 'AGO'),
        (9, 'SEP'),
        (10, 'OCT'),
        (11, 'NOV'),
        (12, 'DIC'),
    ]

    EJERCICIOS = [
        (2016, '2016'),
        (2017, '2017'),
        (2018, '2018'),
        (2019, '2019'),
        (2020, '2020'),
        (2021, '2021'),
    ]

    programa_id = models.ForeignKey(Programa_Padrones, on_delete=models.CASCADE)
    fecha = models.DateField('Fecha', blank=True, null=True)
    tipo = models.CharField('Tipo', max_length=100, blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=255, blank=True, null=True)
    recargos = models.DecimalField('Recargos', decimal_places=2, max_digits=15, blank=True, null=True, default=0)
    accesorios = models.DecimalField('Accesorios', decimal_places=2, max_digits=15, blank=True, null=True, default=0)
    impuesto = models.DecimalField('Impuesto', decimal_places=2, max_digits=15, blank=True, null=True, default=0)
    ejercicio = models.IntegerField('Ejercicio', choices=EJERCICIOS, blank=True, null=True)
    periodo = models.IntegerField('Periodo', choices=PERIODOS, blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    presuntiva = models.BooleanField('Presuntiva', blank=True, null=True, default=False)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Pagos'
        verbose_name_plural = 'Pagos'
        ordering = ['programa_id']

    def __str__(self):
        return str(self.programa_id)


class Programas_Recaudacion(models.Model):
    """ Model Programas Recaudacion """
    
    programa = models.CharField('Programa', max_length=200, blank=True, null=True)
    nombre = models.CharField('Nombre', max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Programas'
        verbose_name_plural = 'Programas'
        
    def __str__(self):
        return self.programa


def update_payments(sender, instance, created, **kwargs):
    print(" ============= Se actualizo Recaudado =========== ")

    if created:
        pk = str(instance.programa_id)

        total = Pagos_Padrones.objects.filter(
            programa_id=pk
        ).aggregate(
            total_recargos=Sum('recargos'), 
            total_accesorios=Sum('accesorios'), 
            total_impuesto=Sum('impuesto')
        )
        recaudado = total['total_recargos'] + total['total_accesorios'] + total['total_impuesto']

        instance = Programa_Padrones.objects.get(pk=pk)
        instance.recaudado = recaudado
        instance.save()

post_save.connect(update_payments, sender=Pagos_Padrones)
