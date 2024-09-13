import unidecode

from django.db import models
from django.db.models.signals import post_save
from django.db.models import Q, Sum
from model_utils.models import TimeStampedModel
from applications.home.models import Codigos_Maestros

from .managers import ProgramaTransferidosManager

class Programa_Transferidos(TimeStampedModel):
    """ Model Programacion """

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
        (2022, '2022'),
    ]


    nuevo_folio = models.CharField(
        'Nuevo Folio', max_length=50, blank=True, null=True)
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
    estatus = models.CharField('Estatus', max_length=400, blank=True, null=True)
    seguimiento = models.CharField(
        'Seguimiento',  max_length=100, blank=True, null=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True, null=True)
    area = models.CharField('Area', max_length=200, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=False)
    comentarios = models.CharField('Comentarios', max_length=600, blank=True, null=True)
    metodo_envio = models.CharField('Metodo Envio', max_length=255, blank=True, null=True)
    ejercicio = models.IntegerField(
        'Ejercicio', choices=EJERCICIOS, blank=True, null=True)
    periodo = models.IntegerField(
        'Periodo', choices=PERIODOS, blank=True, null=True)
    is_close = models.BooleanField('Cerrado', default=False)

    objects = ProgramaTransferidosManager()

    class Meta:
        verbose_name = 'Programacion'
        verbose_name_plural = 'Programacion'
        ordering = ['nuevo_folio']

    def __str__(self):
        # return str(self.id) + '--' + self.rfc + ' ' +  self.nombre + ' ' + self.programa + ' ' + self.estatus
        return str(self.id)


class Detalle_Transferidos(models.Model):
    """ Model Detalle """

    programa_id = models.ForeignKey(
        Programa_Transferidos, on_delete=models.CASCADE, related_name='detalle_programa')
    fecha = models.DateField('Fecha', blank=True, null=True)
    comentarios = models.CharField(
        'Comentarios', max_length=255, blank=True, null=True)
    etapa = models.CharField('Etapa', max_length=50, blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=400, blank=True, null=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalle'
        ordering = ['programa_id']

    def __str__(self):
        return str(self.programa_id)


class Archivos_Transferidos(models.Model):
    """ Model Archivos """

    programa_id = models.ForeignKey(
        Programa_Transferidos, on_delete=models.CASCADE)
    tipo = models.CharField('Tipo', max_length=100, blank=True, null=True)
    fecha = models.DateField('Fecha', blank=True, null=True)
    comentarios = models.CharField(
        'Comentarios', max_length=255, blank=True, null=True)
    archivo = models.FileField(
        'Archivo', upload_to='media/programacion', blank=True, null=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Archivos'
        verbose_name_plural = 'Archivos'
        ordering = ['programa_id']

    def save(self, *args, **kwargs):
        self.archivo.name = str(unidecode.unidecode(self.archivo.name))

        super(Archivos_Transferidos, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.programa_id)


class Pagos_Transferidos(models.Model):
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
        (2017, '2017'),
        (2018, '2018'),
        (2019, '2019'),
        (2020, '2020'),
        (2021, '2021'),
    ]

    programa_id = models.ForeignKey(
        Programa_Transferidos, on_delete=models.CASCADE)
    fecha = models.DateField('Fecha', blank=True, null=True)
    tipo = models.CharField('Tipo', max_length=100, blank=True, null=True)
    comentarios = models.CharField(
        'Comentarios', max_length=255, blank=True, null=True)
    recargos = models.DecimalField(
        'Recargos', decimal_places=2, max_digits=15, blank=True, null=True, default=0)
    accesorios = models.DecimalField(
        'Accesorios', decimal_places=2, max_digits=15, blank=True, null=True, default=0)
    impuesto = models.DecimalField(
        'Impuesto', decimal_places=2, max_digits=15, blank=True, null=True, default=0)
    ejercicio = models.IntegerField(
        'Ejercicio', choices=EJERCICIOS, blank=True, null=True)
    periodo = models.IntegerField(
        'Periodo', choices=PERIODOS, blank=True, null=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True, null=True)
    presuntiva = models.BooleanField(
        'Presuntiva', blank=True, null=True, default=False)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Pagos'
        verbose_name_plural = 'Pagos'
        ordering = ['programa_id']

    def __str__(self):
        return str(self.programa_id)


class Temporal(models.Model):
    """ Model Programacion Temporal"""
   
    rfc = models.CharField(
        'RFC', max_length=30, blank=True
    )
    nombre = models.CharField(
        'Nombre', max_length=200, blank=True, null=True
    )
    direccion = models.CharField(
        'Direccion', max_length=255, blank=True, null=True
    )
    presuntiva = models.DecimalField(
        'Presuntiva', decimal_places=2, max_digits=15, blank=True, null=True
    )
    programa = models.CharField(
        'Programa', max_length=50, blank=True, null=True
    )
    metodo_envio = models.CharField(
        'Metodo Envio', max_length=255, blank=True, null=True
    )
    ejercicio = models.IntegerField(
        'Ejercicio', blank=True, null=True
    )
    periodo = models.IntegerField(
        'Periodo', blank=True, null=True
    )
    estatus = models.CharField(
        'Estatus', max_length=100, blank=True, null=True
    )
    unidad_responsable = models.CharField(
        'Unidad Responsable', max_length=200, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Temporal'
        verbose_name_plural = 'Temporal'
        ordering = ['rfc']

    def __str__(self):
        return self.rfc

class Catalogo(TimeStampedModel):
    llave = models.CharField(  
        'Llave', max_length=200, blank=True, null=True
    )
    valor = models.CharField(  
        'Valor', max_length=200, blank=True, null=True
    )
    etapa = models.CharField(  
        'Llave', max_length=200, blank=True, null=True
    )
    estatus = models.CharField(  
        'Llave', max_length=200, blank=True, null=True
    )
    tipo = models.CharField(  
        'Llave', max_length=200, blank=True, null=True
    )
    is_active = models.BooleanField('estatus',default=True) 


class Impuestos(models.Model):
    """ Model Impuestos """

    contribuyente = models.ForeignKey(
        Programa_Transferidos, on_delete=models.CASCADE, related_name='impuesto_transferidos'
    )
    impuesto = models.ForeignKey(
        Codigos_Maestros, on_delete=models.CASCADE, related_name='impuesto_obligaciones'
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


def insert_detail(sender, instance, created, **kwargs):
    print("  ======== Se guardo detalle ========= ")

    if created:
        obj = Programa_Transferidos.objects.latest('id')
        detail = Detalle_Transferidos(
            programa_id=obj,
            fecha=instance.fecha,
            comentarios='',
            estatus='NUEVO',
        )
        detail.save()


def update_payments(sender, instance, created, **kwargs):
    print(" ============= Se actualizo Recaudado =========== ")

    # if created:
    pk = str(instance.programa_id_id)

    total = Pagos_Transferidos.objects.filter(
        programa_id=pk
    ).aggregate(
        total_recargos=Sum('recargos'),
        total_accesorios=Sum('accesorios'),
        total_impuesto=Sum('impuesto')
    )
    recaudado = total['total_recargos'] + \
        total['total_accesorios'] + total['total_impuesto']

    # print('==============')
    # print(total)

    instance = Programa_Transferidos.objects.get(pk=pk)
    instance.recaudado = recaudado
    instance.save()


#post_save.connect(insert_detail, sender=Programa_Transferidos)
post_save.connect(update_payments, sender=Pagos_Transferidos)
