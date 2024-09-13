import unidecode

from django.db import models
from django.db.models.signals import post_save
from django.db.models import Q, Sum
from model_utils.models import TimeStampedModel
from .managers import ProgramaManager
from applications.home.models import Codigos_Maestros

class Modelos(TimeStampedModel):
    """ Model Modelos """

    nombre = models.CharField('Nombre', max_length=200, unique=True)
    alias = models.CharField('Alias', max_length=200)
    descripcion = models.CharField(
        'Descripcion', max_length=600, blank=True, null=True)
    fecha_inicio = models.DateField('Fecha Inicio', blank=True, null=True)
    estatus = models.BooleanField('Estatus', blank=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True, null=True)
    archivo = models.FileField(
        'Archivo', upload_to='modelos', blank=True, null=True)

    class Meta:
        verbose_name = 'Modelos'
        verbose_name_plural = 'Modelos'
        ordering = ['alias']

    def __str__(self):
        return str(self.alias)
        

class Contribuyentes(TimeStampedModel):
    """ Model Contribuyentes """

    modelo = models.ForeignKey(Modelos, on_delete=models.CASCADE, related_name='contribuyentes_modelo', blank=True, null=True)
    rfc = models.CharField('RFC', max_length=30, blank=True)
    prioridad = models.IntegerField('Prioridad', blank=True, null=True)
    programa = models.CharField('Programa', max_length=50, blank=True, null=True)
    monto = models.DecimalField('Monto', decimal_places=2, max_digits=15, blank=True, null=True, default=0)
    fecha_inicio = models.DateField('Fecha Inicio', blank=True, null=True)
    fecha_fin = models.DateField('Fecha Fin', blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    motivo = models.CharField('Motivo', max_length=50, blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=600, blank=True, null=True)
    is_ready = models.BooleanField('Completo', default=False)

    class Meta:
        verbose_name = 'Contribuyentes'
        verbose_name_plural = 'Contribuyentes'
        ordering = ['rfc']
        
    def __str__(self):
        return self.rfc


class Impuestos(models.Model):
    """ Model Impuestos """

    contribuyente = models.ForeignKey(
        Contribuyentes, on_delete=models.CASCADE, related_name='impuesto_contribuyente'
    )
    impuesto = models.ForeignKey(
        Codigos_Maestros, on_delete=models.CASCADE, related_name='impuesto_impuesto'
    )
    periodo = models.CharField('periodo', max_length=20, blank=True)
    ejercicio = models.IntegerField('año actual',blank=True)
    ejercicio_1 = models.IntegerField('año -1', blank=True)
    ejercicio_2 = models.IntegerField('año -2', blank=True)
    ejercicio_3 = models.IntegerField('año -3', blank=True)
    ejercicio_4 = models.IntegerField('año -4', blank=True)
    ejercicio_5 = models.IntegerField('año -5', blank=True)

    class Meta:
        verbose_name = 'Impuestos'
        verbose_name_plural = 'Impuestos'
        ordering = ['contribuyente']
        
    def __str__(self):
        return str(self.id)


class Programa(TimeStampedModel):
    """ Model Programacion """

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
    interlocutor = models.CharField('Interlocutor', max_length=10, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    seguimiento = models.CharField('Seguimiento',  max_length=100, blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    is_close = models.BooleanField('Cerrado', default=False)

    objects = ProgramaManager()

    class Meta:
        verbose_name = 'Programacion'
        verbose_name_plural = 'Programacion'
        ordering = ['id']
        
    def __str__(self):
        #return str(self.id) + '--' + self.rfc + ' ' +  self.nombre + ' ' + self.programa + ' ' + self.estatus
        return str(self.id)


class Cerrados(models.Model):
    """ Model Cerrados """

    folio = models.CharField('Folio', max_length=50, blank=True, null=True)
    rfc = models.CharField('RFC', max_length=30, blank=True)
    programa = models.CharField(
        'Programa', max_length=50, blank=True, null=True)
    presuntiva = models.DecimalField(
        'Estimado', decimal_places=2, max_digits=15, blank=True, null=True)
    recaudado = models.DecimalField(
        'Recaudado', decimal_places=2, max_digits=15, blank=True, null=True)
    dias = models.PositiveIntegerField(
        'Dias Trasncurridos', blank=True, null=True, default=0)
    nombre = models.CharField('Nombre', max_length=200, blank=True, null=True)
    direccion = models.CharField(
        'Direccion', max_length=255, blank=True, null=True)
    fecha = models.DateField('Fecha', blank=True, null=True)
    etapa = models.CharField('Etapa', max_length=50, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    seguimiento = models.CharField(
        'Seguimiento',  max_length=100, blank=True, null=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True, null=True)
    area = models.CharField('Area', max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Cerrados'
        verbose_name_plural = 'Cerrados'
        ordering = ['id']

    def __str__(self):
        return str(self.id)
        

class Detalle(models.Model):
    """ Model Detalle """

    programa_id = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='detalle_programa')
    fecha = models.DateField('Fecha', blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=600, blank=True, null=True)
    etapa = models.CharField('Etapa', max_length=50, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalle'
        ordering = ['programa_id']

    def __str__(self):
        return str(self.programa_id_id)


class Archivos(models.Model):
    """ Model Archivos """

    programa_id = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='archivos_programa')
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

        super(Archivos, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.programa_id)



class Archivos_Contribuyente(models.Model):
    """ Model Archivos """

    contribuyente = models.ForeignKey(Contribuyentes, on_delete=models.CASCADE, related_name='archivos_contribuyentes')
    tipo = models.CharField('Tipo', max_length=100, blank=True, null=True)
    fecha = models.DateField('Fecha', blank=True, null=True)
    comentarios = models.CharField('Comentarios', max_length=255, blank=True, null=True)
    archivo = models.FileField('Archivo', upload_to='media/programacion', blank=True, null=True)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Archivos Contribuyente'
        verbose_name_plural = 'Archivos Contribuyente'
        ordering = ['contribuyente']

    def save(self, *args, **kwargs):
        self.archivo.name = str(unidecode.unidecode(self.archivo.name))

        super(Archivos_Contribuyente, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.programa_id)


class Pagos(models.Model):
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
        (2023, '2023'),
        (2022, '2022'),
        (2021, '2021'),
        (2020, '2020'),
        (2019, '2019'),
        (2018, '2018'),
        (2017, '2017'),
        # (2016, '2016'),
    ]

    programa_id = models.ForeignKey(Programa, on_delete=models.CASCADE)
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



def insert_detail(sender, instance, created, **kwargs):
    if created:
        obj = Programa.objects.latest('id')
        detail = Detalle(
            programa_id=obj,
            fecha=instance.fecha,
            comentarios='',
            estatus='NUEVO',
        )
        detail.save()


def update_payments(sender, instance, created, **kwargs):
    pk = str(instance.programa_id)

    total = Pagos.objects.filter(
        programa_id=pk,
        is_active=True
    ).aggregate(
        total_recargos=Sum('recargos'), 
        total_accesorios=Sum('accesorios'), 
        total_impuesto=Sum('impuesto')
    )
    recaudado = total['total_recargos'] + total['total_accesorios'] + total['total_impuesto']

    instance = Programa.objects.get(pk=pk)
    instance.recaudado = recaudado
    instance.save()


post_save.connect(insert_detail, sender=Programa)
post_save.connect(update_payments, sender=Pagos)




    