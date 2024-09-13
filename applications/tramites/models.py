from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField 
from applications.users.models import User, Areas
from model_utils.models import TimeStampedModel


class Tipos(models.Model):
    tipo = models.CharField('Tipo', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Tipo'
        verbose_name_plural = 'Tipos'

    def __str__(self):
        return str(self.tipo)


class Tramite(models.Model):
    tipo_tramite = models.CharField('Tipo Tramite', max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Tramite'
        verbose_name_plural = 'Tramites'

    def __str__(self):
        return str(self.tipo_tramite) 


class Estatus(models.Model):
    esta_tus = models.CharField(max_length=50,blank=True,null=True)
    
    class Meta:
        verbose_name = 'Estatus'
        
    def __str__(self):
        return str(self.esta_tus) 
    
    def Estado(self):
        if self.tramite:
            return str(self.esta_tus)
        else:   
            return ''


class NuevoTramite(models.Model):
    confianza = models.BooleanField(default=False,blank=True, null=True)
    honorarios = models.BooleanField(default=False, blank=True, null=True)
    plaza = models.BooleanField(default=False, blank=True, null=True)
    linea = models.BooleanField(default=False, blank=True, null=True)
    presencial = models.BooleanField(default=False, blank=True, null=True)
    estatus = models.ForeignKey(Estatus,on_delete=models.CASCADE,related_name='estatus',blank=True,null=True)
    tramite = models.ForeignKey(Tramite,on_delete=models.CASCADE,related_name='tramite',blank=True, null=True)
    titulo_formato = RichTextUploadingField(default='q',blank=True, null=True)   
    servicio = models.CharField('Servicio',max_length=100,blank=True, null=True)
    tipo = models.ForeignKey(Tipos,on_delete=models.CASCADE, related_name='tipos',blank=True, null=True)
    comentarios = models.CharField('Comentarios',max_length=100,blank=True,null=True)
    is_active = models.BooleanField("Activo",default=True)
    asignar_a = models.ManyToManyField(
      User, related_name="Asignar", blank=True  
    )

    class Meta: 
        verbose_name = 'Tramite nuevo'   
        verbose_name_plural = 'Tramites nuevos'
        # ordering = ['nombre']

    def __str__(self):
        return str(self.servicio) 

    def Tramites(self):
        if self.tramite:
            return str(self.tramite)
        else:   
            return ''

    def Estado(self):
        if self.estatus:
            return str(self.estatus)
        else:   
            return 'Modificado'

    def datosTotals(self): 
        return Solicitud.objects.filter(tramite=self.id).count()
    
    def datosEnviados(self): 
        return Solicitud.objects.filter(estatus__nombre='ENVIADA', tramite=self.id).count()
    
    def datosAcptados(self): 
        return Solicitud.objects.filter(estatus__nombre='ACEPTADA', tramite=self.id).count()


class Observaciones(models.Model):
    detalle = models.CharField('Observaciones',max_length=200,blank=True,null=True)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,related_name='usuario_observaciones')
    fecha_realizada = models.DateField(auto_now_add=True,null=True)
    is_active = models.BooleanField("Activo",default=True)
    tramite = models.ForeignKey(NuevoTramite,on_delete=models.CASCADE,related_name='nuevo_tramite_observaciones',blank=True,null=True)
   
    class Meta:
        verbose_name = 'Observaciones'
        verbose_name_plural = 'Observaciones'

    def __str__(self):
        return str(self.detalle)


class Requisitos(TimeStampedModel):
    nombre = models.CharField("Nombre", max_length=255)
    obligatorio = models.BooleanField("Obligatorio", default=False)
    tiene_formato_default = models.BooleanField("¿Tiene formato por defecto?", default=False)
    ruta_formato = models.CharField("URL", max_length=500, null=True, blank=True)
    ruta_nombre_archivo = models.CharField("Nombre archivo", max_length=500, null=True, blank=True)
    tramite = models.ForeignKey(NuevoTramite, on_delete=models.CASCADE, related_name="tramite_requisitos", null=True, blank=True)

    class Meta:
        verbose_name = 'Requisito tramite' 
        verbose_name_plural = 'Requesitos tramite'
    
    def __str__(self):
        return self.nombre


class Estatus_Solicitud(TimeStampedModel):
    nombre = models.CharField("Descripción", max_length=500)
    is_active = models.BooleanField("Activo")

    class Meta:
        verbose_name = "Estatus solicitud"
        verbose_name_plural = "Estatus solicitudes"
    
    def __str__(self):
        return nombre


class Solicitud(TimeStampedModel): 
    folio = models.CharField("Folio", max_length=15, null=True, blank=True)
    tramite = models.ForeignKey(NuevoTramite, on_delete=models.CASCADE, related_name="tramite_solicitud_tramite")
    vigencia = models.IntegerField("Vigencia", null=True, blank=True)
    fecha_inicio = models.DateField("Fecha de inicio", null=True, blank=True)
    fecha_vigencia = models.DateField("Fecha de vigencia", null=True, blank=True)
    fecha_fin = models.DateField("Fecha final", null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_solicitud_tramite")
    observaciones = models.CharField("Observaciones", max_length=600, null=True, blank=True)
    estatus = models.ForeignKey(Estatus_Solicitud, on_delete=models.CASCADE, related_name="estatus_solicitud_tramite")
    usuario_reviso = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_reviso_solicitud_tramite", null=True, blank=True)
    usuario_autorizo = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_autorizo_solicitud_tramite", null=True, blank=True)
    usuario_asignado = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_asignado_solicitud_tramite", null=True, blank=True)

    class Meta:
        verbose_name = "Solicitud de trámites"
        verbose_name_plural = "Solicitudes de trámites"
    
    def __str__(self):
        return str(self.tramite.servicio) + " : " +  str(self.usuario) + " " + self.fecha_inicio.strftime("%d/%m/%Y") + " al " + self.fecha_fin.strftime("%d/%m/%Y")


class Detalle_Solicitud(TimeStampedModel):
    requisito = models.ForeignKey(Requisitos, on_delete=models.CASCADE, related_name="requisito_detalle_solicitud", null=True, blank=True)
    requisito_nombre = models.CharField("Requisito", max_length=600, null=True, blank=True)
    es_obligatorio = models.BooleanField("¿Es obligatorio?")
    nombre_archivo = models.CharField("Nombre archivo", max_length=500, null=True, blank=True)
    ruta_archivo = models.CharField("Ruta archivo", max_length=600, null=True, blank=True)
    estatus = models.CharField("Estatus", max_length=255)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_detalle_solicitud_tramite")
    solicitud_tramite = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name="detalle_solicitudes_tramites")
    folio_temporal = models.CharField("Folio Temporal", max_length=15, null=True, blank=True)
    observaciones = models.CharField("Observaciones", max_length=600, null=True, blank=True)

    class Meta:
        verbose_name = "Detalle solicitud trámite"
        verbose_name_plural = "Detalles solicitud trámite"
    
    def __str__(self):
        return str(self.solicitud_tramite.tramite.servicio) + " : " + self.requisito_nombre


class Detalle_solicitud_temporal(TimeStampedModel):
    folio = models.CharField("Folio", max_length=15)
    requisito = models.ForeignKey(Requisitos, on_delete=models.CASCADE, related_name="requisito_detalle_solicitud_tmp")
    requisito_nombre = models.CharField("Requisito", max_length=600)
    es_obligatorio = models.BooleanField("¿Es obligatorio?")
    nombre_archivo = models.CharField("Nombre archivo", max_length=500, null=True, blank=True)
    ruta_archivo = models.CharField("Ruta archivo", max_length=600, null=True, blank=True)
    estatus = models.CharField("Estatus", max_length=255)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_detalle_tmp_solicitud_tramite")
    solicitud_tramite = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name="detalle_tmp_solicitudes_tramites", null=True, blank=True)
    observaciones = models.CharField("Observaciones", max_length=600, null=True, blank=True)

    class Meta:
        verbose_name = "Temporal detalle solicitud trámite"
        verbose_name_plural = "Temporal detalles solicitud trámite"
    
    def __str__(self):
        return self.folio  + " : " + str(self.solicitud_tramite.tramite.servicio)


class Historial_Solicitudes(TimeStampedModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_historial_solicitudes")
    solicitud_tramite = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name="solicitud_historial_solicitudes")
    observaciones = models.CharField("Observaciones", max_length=600, null=True, blank=True)
    estatus = models.ForeignKey(Estatus_Solicitud, on_delete=models.CASCADE, related_name="estatus_historial_solicitud")
    detalle_solicitud_tramite = models.ForeignKey(Detalle_Solicitud, on_delete=models.CASCADE, related_name="detalle_solicitud_historial_solicitudes", null=True, blank=True)
    estatus_detalle_solicitud = models.CharField("Estatus detalle solicitud", max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Historial solicitud"
        verbose_name_plural = "Historial solicitudes"

    def __str__(self):
        return str(self.solicitud_tramite.tramite.servicio) + " : " + self.estatus.nombre + "(" + self.usuario.username + ")"
