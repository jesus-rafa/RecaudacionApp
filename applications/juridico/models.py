import unidecode

from applications.users.models import User
from applications.home.models import Municipio
from django.db import models
from django.db.models.signals import post_save
from model_utils.models import TimeStampedModel

# Create your models here.
class Demanda(TimeStampedModel):
    carpeta = models.CharField('Carpeta', max_length=300)
    juicio = models.ForeignKey(
        'Catalogo', on_delete=models.CASCADE, related_name="tipo_Juicio"
    )
    subtipo = models.ForeignKey(
        'Catalogo', on_delete=models.CASCADE, related_name="tipo_Demanda"
    )
    expediente = models.CharField('Expediente', max_length=300)
    tribunal = models.ForeignKey(
        'Catalogo', blank=True, null=True, on_delete=models.CASCADE, related_name="tribunal_Demanda"
    )
    #models.CharField('Tribunal', max_length=300, blank=True, null=True)
    fecha_aviso = models.DateField('Aviso', blank=True, null=True)
    fecha_notificacion = models.DateField(
        'Notificacion', blank=True, null=True)
    fecha_interno = models.DateField('Interno', blank=True, null=True)
    fecha_fatal = models.DateField('Fatal', blank=True, null=True)
    # dictaminador =  models.ManyToManyField(
    #     User, related_name="dictaminadorl_Demanda"
    # )
    dictaminador = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="dictaminador_Demanda"
    )
    estado_procesal = models.ForeignKey(
        'Catalogo', on_delete=models.CASCADE, related_name="proceso_Demanda"
    )
    autoridad = models.ForeignKey(
        'Catalogo', blank=True, null=True, on_delete=models.CASCADE, related_name="autoridadDemanda"
    )
    resolucion_impg = models.CharField('Resolucion_Impg', blank=True, null=True, max_length=2000)
    cuantia = models.DecimalField('Cuantia', blank=True, null=True, max_digits=12, decimal_places=2)
    materia = models.ForeignKey(
        'Catalogo', blank=True, null=True, on_delete=models.CASCADE, related_name="materiaDemanda"
    )
    contribuyente = models.CharField(
        'Contribuyente', max_length=200, blank=True, null=True)
    abogado_prom = models.ForeignKey(
        'Catalogo', blank=True, null=True, on_delete=models.CASCADE, related_name="abogadoPromovente"
    )
    #models.CharField('Abogado_Prom', max_length=200, blank=True, null=True)
    fecha_resolucion = models.DateField('Resolucion', blank=True, null=True)
    resolucion_rec = models.CharField(
        'Resolucion_Rec', max_length=200, blank=True, null=True)
    autoridad_rec = models.ForeignKey(
        'Catalogo', blank=True, null=True, on_delete=models.CASCADE, related_name="recurridaDemanda"
    )
    fecha_contestacion = models.DateField(
        'Contestacion', blank=True, null=True)
    oficio = models.CharField('Oficio', max_length=300, blank=True, null=True)
    rfc = models.CharField('Rfc', max_length=15, blank=True, null=True)
    resolucion = models.BooleanField('resolucion', blank=True, null=True)
    is_active = models.BooleanField('estatus', default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="creacion_Demanda"
    )

    class Meta:
        verbose_name = 'Demanda'
        verbose_name_plural = 'Demandas'

    def __str__(self):
        return str(self.id)

class Catalogo(models.Model):
    nombre = models.CharField('Nombre', max_length=300)
    valor = models.CharField('Valor', blank=True, null=True, max_length=100)
    auxiliar = models.CharField(
        'Auxiliar', blank=True, null=True, max_length=100)
    padre = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE, related_name="hijo"
    )
    sort = models.IntegerField('Sort', blank=True, null=True)
    agrupador = models.CharField('Agrupador', max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Catalogo'
        verbose_name_plural = 'Catalogos'
        ordering = ['sort']

    def __str__(self):
        return self.nombre


class Formulario(models.Model):
    etiqueta = models.CharField('Etiqueta', max_length=254)
    campo = models.CharField('Campo', max_length=254)
    tipo_control = models.CharField('Tipo Control', max_length=254)
    is_visible = models.BooleanField('Visible', default=True)
    is_required = models.BooleanField('Requerido', default=True)
    consulta = models.CharField('Consulta', max_length=500, blank=True, null=True)
    plantilla_form = models.CharField('plantilla_form', max_length=100,blank=True, null=True)
    
    class Meta:
        verbose_name = 'Formulario'
        verbose_name_plural = 'Formularios'
        ordering = ['id']

    def __str__(self):
        return  self.etiqueta


class Rubros(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    interno = models.IntegerField('Valor', blank=True, null=True)
    fatal = models.IntegerField('Auxiliar', blank=True, null=True)
    sort = models.IntegerField('Sort', blank=True, null=True)
    agrupador = models.CharField('Agrupador', max_length=100)
    formulario = models.CharField('Formulario', max_length=100,blank=True, null=True)
    is_active = models.BooleanField(default=True)
    etapa = models.ForeignKey(
        Catalogo, blank=True, null=True, on_delete=models.CASCADE, related_name="rubro_catalogo"
    )
    etapa_siguiente = models.ForeignKey(
        Catalogo, blank=True, null=True, on_delete=models.CASCADE, related_name="rubro_etapa_siguiente"
    )

    class Meta:
        verbose_name = 'Rubro'
        verbose_name_plural = 'Rubros'
        ordering = ['sort']

    def __str__(self):
        return self.nombre


class Proceso(TimeStampedModel):
    rubro = models.ForeignKey(
        Rubros, on_delete=models.CASCADE, related_name="rubro_proceso"
    )
    demanda = models.ForeignKey(
        Demanda, on_delete=models.CASCADE, related_name="demanda_proceso"
    )
    etapa = models.ForeignKey(
        Catalogo, on_delete=models.CASCADE, related_name="etapa_proceso"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="creacion_proceso"
    )
    padre = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE, related_name="hijo"
    )
    fecha_aviso = models.DateField('proceso_aviso', blank=True, null=True)
    fecha_notificacion = models.DateField('proceso_notificacion', blank=True, null=True)
    fecha_interno = models.DateField('proceso_interno', blank=True, null=True)
    fecha_fatal = models.DateField('proceso_fatal', blank=True, null=True)
    fecha_cierre = models.DateField('proceso_cierre', blank=True, null=True)
    is_active = models.BooleanField('estatus', default=True)

    class Meta:
        verbose_name = 'Proceso'
        verbose_name_plural = 'Proceso'
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class Proceso_Detalle(TimeStampedModel):
    """ Model Proceso_Detalle """
    folio = models.PositiveIntegerField('Folio', blank=True)
    id_proceso = models.ForeignKey(
        Proceso, on_delete=models.CASCADE
    )
    dato = models.CharField('Datos', max_length=254, blank=True)
    valor = models.CharField('Valor', max_length=500, blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="creacion_detalle"
    )
    archivo = models.FileField(
        'Archivo', upload_to='juridico/', blank=True, null=True)

    class Meta:
        verbose_name = 'Proceso Detalle'
        verbose_name_plural = 'Proceso Detalle'
        ordering = ['id_proceso']

    def __str__(self):
        return str(self.folio)


class Archivos_Juridico(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE)
    archivo = models.FileField(
        blank=True,
        upload_to='juridico/%Y/%m/%d/',
        verbose_name="archivo"
    )

    def save(self, *args, **kwargs):
        self.archivo.name = str(unidecode.unidecode(self.archivo.name))

        super(Archivos_Juridico, self).save(*args, **kwargs)

class Solicitante(TimeStampedModel):
    rfc = models.CharField('Rfc', max_length=15)#blank=True, null=True
    nombre = models.CharField('Nombre', max_length=200)#blank=True, null=True
    apeP = models.CharField('ApeP', max_length=50)#blank=True, null=True
    apeM = models.CharField('ApeM', max_length=50)#blank=True, null=True
    calle = models.CharField('calle', max_length=200)#blank=True, null=True
    numero = models.IntegerField('numero')
    colonia = models.CharField('colonia', max_length=200)#blank=True, null=True
    ciudad = models.CharField('ciudad', max_length=200)#blank=True, null=True
    cp = models.IntegerField('cp')
    telefono = models.BigIntegerField('telefono')
    activo = models.BooleanField('activo', default=True)

    class Meta:
        verbose_name = 'Solicitante'
        verbose_name_plural = 'Solicitantes'
        ordering = ['id']

    def __str__(self):
        return str(self.rfc)

class Resolutor(TimeStampedModel):
    carpeta = models.CharField('Carpeta', max_length=300)
    oficio = models.CharField('Oficio', max_length=300) #blank=True, null=True
    fecha_presentacion = models.DateField('Fecha_presentacion') #, blank=True, null=True
    fecha_resolucion = models.DateField('Fecha_resolucion', blank=True, null=True) #, blank=True, null=True
    concepto = models.ForeignKey(
      Catalogo, on_delete=models.CASCADE, related_name="Concepto", blank=True, null=True
    )
    solicitante =  models.ForeignKey(
      Solicitante, on_delete=models.CASCADE, related_name="solicitante_resolutor", blank=True, null=True
    )
    ejercicio_ini = models.CharField('ejercicio_ini',max_length=500,blank=True, null=True)
    ejercicio_fin = models.CharField('ejercicio_fin',max_length=500,blank=True, null=True)
    # caducidad = models.ForeignKey(
    #   Catalogo, on_delete=models.CASCADE, related_name="Caducidad"
    # )
    marca = models.CharField('Marca', max_length=300)
    modelo = models.CharField('Modelo', max_length=300)
    serie = models.CharField('Serie', max_length=300)
    placa = models.CharField('Placa', max_length=300)
    documentacion = models.ForeignKey(
      Catalogo, on_delete=models.CASCADE, related_name="Documentacion", blank=True, null=True
    )
    sentido = models.ForeignKey(
      Catalogo, on_delete=models.CASCADE, related_name="Sentido", blank=True, null=True
    )
    formato = models.ForeignKey(
      Catalogo, on_delete=models.CASCADE, related_name="Formato", blank=True, null=True
    )
    fecha_notificacion = models.DateField('Fecha_notificacion', blank=True, null=True) #, blank=True, null=True=
    titular = models.ForeignKey(
      User, on_delete=models.CASCADE, related_name="titular", blank=True, null=True
    )
    municipio = models.ForeignKey(
      Municipio, on_delete=models.CASCADE, related_name="Municipio", null=True, blank=True
    )
    # abogado = models.ManyToManyField(
    #   User, related_name="abogados_resolutor", blank=True
    # )
    abogado = models.ForeignKey(
      User, on_delete=models.CASCADE, related_name="abogado_resolutor", null=True, blank=True
    )
    monto = models.IntegerField('monto',blank=True, null=True)
    activo = models.BooleanField('activo', default=True)


    class Meta:
        verbose_name = 'Resolutor'
        verbose_name_plural = 'Resolutores'
        ordering = ['id']

    def __str__(self):
        return str(self.id)

class Requisitos(TimeStampedModel):
    nombre          = models.CharField("Nombre", max_length=255)
    obligatorio     = models.BooleanField("Obligatorio", default=False)
    formato_default = models.BooleanField("Formato por defecto", default=False)
    # ruta            = models.CharField("URL", max_length=500, null=True, blank=True)
    # nombre_archivo  = models.CharField("Nombre archivo", max_length=500, null=True, blank=True)
    archivo         = models.FileField('Archivo', upload_to='juridico/resolutor/%Y/', blank=True, null=True)
    tramite         = models.ForeignKey(Catalogo, on_delete=models.CASCADE, related_name="tramite", null=True, blank=True)
    activo          = models.BooleanField('activo', default=True)
    
    class Meta:
        verbose_name = 'Requisito' 
        verbose_name_plural = 'Requisitos'
    
    def __str__(self):
        return str(self.nombre)
    
    def get_absolute_url(self):
        return reverse('juridico_app:resolutorRequisito-actualiza', args=[str(self.id)])

class Resolutor_detalle(models.Model):
    resolutor   = models.ForeignKey(Resolutor, on_delete=models.CASCADE, related_name="detalle_resolutor")
    comentarios = models.CharField('comentarios', max_length=300)
    etapa       = models.ForeignKey(Catalogo, on_delete=models.CASCADE, related_name="detalle_etapa")
    estatus     = models.ForeignKey(Catalogo, on_delete=models.CASCADE, related_name="detalle_estatus")
    usuario     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="detalle_usuario")
    created     = models.DateField(auto_now_add=True)
    updated     = models.DateField(auto_now=True)
    archivo     = models.FileField('Archivo', upload_to='juridico/resolutor/%Y/', blank=True, null=True)
    requisito   = models.ForeignKey(Requisitos, on_delete=models.CASCADE, related_name="resolutor_requisito", null=True, blank=True)
    activo      = models.BooleanField('activo', default=True)

    class Meta:
        verbose_name = 'Resolutor_detalle'
        verbose_name_plural = 'Resolutores_detalle'
        ordering = ['id']

    def __str__(self):
        return str(self.id)

def insert_detail(sender, instance, created, **kwargs):

#    agrupa = str(instance.juicio_id) + '_' + str(instance.subtipo_id)

#    instance_rubro = Rubros.objects.get(agrupador = agrupa, etapa_id = 2)
    instance_rubro_create = Rubros.objects.get(id = 137)
#    print(instance_rubro)
    instance_catalog = Catalogo.objects.get(agrupador = 'ESTADO_PROCESAL', sort = 0)

    if created:
        detail = Proceso(
            rubro=instance_rubro_create,
            demanda=instance,
            etapa=instance_catalog,
            created_by = instance.created_by,
            fecha_aviso = instance.fecha_aviso,
            fecha_notificacion = instance.fecha_notificacion,
            fecha_interno = instance.fecha_interno,
            fecha_fatal = instance.fecha_fatal,
        )
        detail.save()
        instance_proceso = Proceso.objects.latest('id')

        proceso_detalle = Proceso_Detalle(
            folio= 0,
            id_proceso = instance_proceso,
            dato = 'comentario',
            valor = 'Se crea la demanda con numero de carpeta: ' + str(instance.carpeta),
            created_by = instance.created_by,
        )
        proceso_detalle.save()

post_save.connect(insert_detail, sender=Demanda)

def desactiva_Solicitante(instance, created, **kwargs):
    
    if created:
        Solicitante.objects.filter(rfc = instance.rfc, activo = True).update(activo = False)
        Solicitante.objects.filter(pk = instance.pk).update(activo = True)

post_save.connect(desactiva_Solicitante, sender=Solicitante)

def enlaza_Requisitos(instance, created, **kwargs):    
    if created:
        requisitos = Requisitos.objects.filter(activo = True)
        for req in requisitos:
            instaceDetalle = Resolutor_detalle.objects.create(
                resolutor=instance,
                comentarios="",
                etapa=Catalogo.objects.get(nombre="DOCUMENTACION"),
                estatus=Catalogo.objects.get(nombre="Creacion"),
                usuario=User.objects.get(pk=76),
                archivo = None,
                requisito = req
            )
        Resolutor_detalle.objects.create(
            resolutor=instance,
            comentarios="Reporte firmado",
            etapa=Catalogo.objects.get(nombre="Concluido"),
            estatus=Catalogo.objects.get(nombre="Concluido"),
            usuario=User.objects.get(pk=76),
            archivo=None,
            requisito=None
        )
        Solicitante.objects.filter(pk=instance.solicitante.pk).update(activo = False)

post_save.connect(enlaza_Requisitos, sender=Resolutor)