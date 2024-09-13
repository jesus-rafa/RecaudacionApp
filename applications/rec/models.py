import os
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings

from applications.programacion.models import Programa
from applications.users.models import User
from .managers import ContactoManager, RECManager
from .coordinates import get_exif_location, get_exif_data
from .signals import optimize_image
from model_utils.models import TimeStampedModel


class Fiscalizados(TimeStampedModel):
    rfc = models.CharField('RFC', max_length=20, unique=True)
    fecha_alta = models.DateField('Fecha', blank=True)
    is_active = models.BooleanField('Estatus', default=True)
    usuario = models.CharField('Usuario', max_length=100, blank=True)

    class Meta:
        verbose_name = 'RFC No Fiscalizados'
        verbose_name_plural = 'Fiscalizados'
        ordering = ['rfc']

    def __str__(self):
        return self.rfc
        
        

class REC(models.Model):
    """ Model REC """

    rfc = models.CharField('RFC', max_length=20, unique=True)
    correo = models.EmailField('Correo', max_length=100, blank=True, null=True)
    telefono = models.CharField('Telefono', max_length=20, blank=True, null=True)
    nombre = models.CharField('Nombre', max_length=254, blank=True, null=True)
    direccion = models.CharField('Direccion', max_length=254, blank=True, null=True)
    fecha_alta = models.DateField('Fecha Alta', blank=True, null=True)

    objects = RECManager()

    class Meta:
        verbose_name = 'REC'
        verbose_name_plural = 'REC'
        ordering = ['rfc']
        
    def __str__(self):
        return str(self.rfc)


class REC_Notificados(TimeStampedModel):
    """ Model REC """

    rfc = models.CharField('RFC', max_length=20, unique=True)
    nombre = models.CharField('Nombre', max_length=254, blank=True, null=True)
    direccion = models.CharField('Direccion', max_length=254, blank=True, null=True)

    class Meta:
        verbose_name = 'REC Notificados'
        verbose_name_plural = 'REC Notificados'
        ordering = ['rfc']
        
    def __str__(self):
        return self.rfc
        
        
class Busquedas(models.Model):
    busqueda = models.CharField('Busqueda', max_length=200, blank=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True)
    fecha = models.DateField('Fecha', blank=True)
    is_success = models.BooleanField('Exito', blank=True, default=False)

    class Meta:
        verbose_name = 'Busquedas'
        verbose_name_plural = 'Busquedas'
        ordering = ['busqueda']

    def __str__(self):
        return self.busqueda
        
        
        
class Registro_Civil(models.Model):
    busqueda = models.CharField('Busqueda', max_length=500, blank=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True)
    fecha = models.DateField('Fecha', blank=True)
    is_success = models.BooleanField('Exito', blank=True, default=False)

    class Meta:
        verbose_name = 'Registro_Civil'
        verbose_name_plural = 'Registro_Civil'
        ordering = ['busqueda']

    def __str__(self):
        return self.busqueda
        
        

class Contacto(models.Model):
    """ Model Contacto """

    rfc = models.ForeignKey(REC, on_delete=models.CASCADE)
    programa_id = models.ForeignKey(Programa, on_delete=models.CASCADE, blank=True, null=True)
    correo = models.EmailField('Correo', max_length=100, blank=True, null=True)
    telefono = models.CharField('Telefono', max_length=20, blank=True, null=True)
    ext = models.CharField('Extension', max_length=10, blank=True, null=True)
    fecha_alta = models.DateField('Fecha', blank=True, null=True)
    nombre = models.CharField('Contacto', max_length=254, blank=True, null=True)
    puesto = models.CharField('Puesto', max_length=254, blank=True, null=True)
    direccion = models.CharField('Direccion', max_length=254, blank=True, null=True)
    imagen = models.ImageField('Imagen', upload_to='media/contacto', blank=True, null=True)
    coordenada = models.CharField('Coordenada', max_length=60, blank=True, null=True)
    visible = models.BooleanField(blank=True, null=True, default=False)
    actualizado = models.BooleanField(blank=True, null=True, default=False)
    usuario = models.CharField('Usuario',  max_length=100, blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    objects = ContactoManager()

    def save(self, *args, **kwargs):
        if self.imagen:
            base_dir = settings.MEDIA_ROOT + '/media/contacto/'
            path = os.path.join(base_dir, str(self.imagen))
            lat, long = get_exif_location(get_exif_data(path))

            if lat == None:
                lat = '-'

            if long == None:
                long = '-'

            self.coordenada = str(lat) + ',' + str(long)
        
        super(Contacto, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contacto'
        ordering = ['rfc']
        
    def __str__(self):
        return str(self.rfc)


class BP(models.Model):
    """ Model Obligaciones """

    rfc = models.ForeignKey(REC, on_delete=models.CASCADE)
    parter = models.CharField('Parter', max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = 'BP'
        verbose_name_plural = 'BP'
        ordering = ['rfc']
        
    def __str__(self):
        return str(self.rfc)


class Obligaciones(models.Model):
    """ Model Obligaciones """

    rfc = models.ForeignKey(REC, on_delete=models.CASCADE)
    obligacion = models.CharField('Obligacion', max_length=254, blank=True, null=True)
    fecha_alta = models.DateField('Fecha Alta', blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    objeto = models.CharField('Objeto', max_length=50, blank=True, null=True)
    fecha_bloqueo = models.DateField('Fecha Bloqueo', blank=True, null=True)
    oc = models.CharField('OC', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Obligaciones'
        verbose_name_plural = 'Obligaciones'
        ordering = ['rfc']
        
    def __str__(self):
        return str(self.rfc)


class Cartas_Invitacion(models.Model):
    """ Model Cartas Invitacion """

    folio = models.CharField('Folio', max_length=50, blank=True)
    rfc = models.CharField('RFC', max_length=30, blank=True)
    programa = models.CharField(
        'Programa', max_length=50, blank=True, null=True)
    resultado = models.CharField(
        'Nombre', max_length=300, blank=True, null=True)
    fecha_envio = models.DateField('Fecha', blank=True, null=True)
    estatus = models.CharField('Estatus', max_length=50, blank=True, null=True)
    usuario = models.CharField(
        'Usuario',  max_length=100, blank=True, null=True)
    remesa = models.CharField(
        'Remesa',  max_length=100, blank=True, null=True)


class Circulo_Credito(TimeStampedModel):
    # Model Círculo Crédito
    rfc = models.CharField("RFC", max_length=13, null=True, blank=True)
    tipo_persona = models.CharField("Tipo Persona", max_length=1, null=True, blank=True)
    numero_cuenta = models.CharField("Número Cuenta", max_length=255, null=True, blank=True)
    razon_social = models.CharField("Razón Social", max_length=200, null=True, blank=True)
    nombre = models.CharField("Nombre", max_length=250, null=True, blank=True)
    apellido_paterno = models.CharField("Apellido Paterno", max_length=250, null=True, blank=True)
    apellido_materno = models.CharField("Apellido Materno", max_length=250, null=True, blank=True)
    curp = models.CharField("CURP", max_length=18, null=True, blank=True)
    fecha_nacimiento = models.DateField("Fecha Nacimiento / Constitución", null=True, blank=True)
    sexo = models.CharField("Sexo", max_length=1, null=True, blank=True)
    nacionalidad = models.CharField("Nacionalidad", max_length=2, null=True, blank=True)
    calle = models.CharField("Calle", max_length=255, null=True, blank=True)
    numero_ext = models.CharField("Numero ext", max_length=30, null=True, blank=True)
    numero_int = models.CharField("Numero int", max_length=30, null=True, blank=True)
    colonia = models.CharField("Colonia", max_length=255, null=True, blank=True)
    municipio = models.CharField("Municipio", max_length=255, null=True, blank=True)
    ciudad = models.CharField("Ciudad", max_length=255, null=True, blank=True)
    estado = models.CharField("Estado", max_length=25, null=True, blank=True)
    cp = models.CharField("Codigo Postal", max_length=5, null=True, blank=True)
    telefono = models.CharField("Telefono", max_length=20, null=True, blank=True)
    adeudo = models.DecimalField("Adeudo", max_digits=15, decimal_places=2, null=True, blank=True)
    fecha_alta = models.DateField("Fecha Alta", null=True, blank=True)
    fecha_ultimo_pago = models.DateField("Fecha Último Pago", null=True, blank=True)
    correo = models.CharField("Correo Electrónico", max_length=250, null=True, blank=True)
    interlocutor = models.CharField("Interlocutor", max_length=50, null=True, blank=True)
    objeto_contrato = models.CharField("Objeto Contrato", max_length=50, null=True, blank=True)
    clave = models.CharField("Clave", max_length=4, null=True, blank=True)
    sub_clave = models.CharField("Sub Clave", max_length=4, null=True, blank=True)
    importe_baja = models.DecimalField("Importe Baja", max_digits=15, decimal_places=2, null=True, blank=True)
    periodo = models.IntegerField("Periodo", default=0)
    ejercicio = models.IntegerField("Ejercicio", default=0)
    usuario = models.CharField("Usuario", max_length=100, null=True, blank=True)
    area = models.CharField("Área", max_length=200, null=True, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    descripcion = models.CharField("Descripcion", max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "circulo_credito"
        verbose_name_plural = "circulo_creditos"

    def __str__(self):
        return str(self.rfc)

    def RazonSocial(self):
        if self.razon_social:
            return str(self.razon_social)
        else:
            return '-'

    def get_contribuyente(self):
        if self.razon_social:
            return self.razon_social
        elif self.nombre:
            return self.nombre + " " + self.apellido_paterno + " " + self.apellido_materno
        else:
            return "-"

    def get_tipo_persona(self):
        if self.tipo_persona == "F":
            return "Person física"
        else:
            return "Persona moral"
    
    def get_period(self):
        return str(self.periodo).rjust(2, '0')

    def PersonaFisica(self):  
        if self.nombre or self.razon_social:    
            return self.razon_social or self.nombre
        else:
            return '-'

    def Correo(self):
        if self.correo:
            return self.correo
        else:
            return '-'

    def Curp(self):
        if self.curp:
            return self.curp
        else:
            return '-'

    def Telefono(self):
        if self.telefono:
            return self.telefono
        else:
            return '-'
    
    def SubClave(self):
        if self.sub_clave:
            return self.sub_clave
        else:
            return '-'

    def Sexo(self):
        if self.sexo:
            return self.sexo
        else:
            return '-'

    def FechaNacimiento(self):
        if self.fecha_nacimiento:
            return self.fecha_nacimiento
        else:
            return '-'


class Temporal_Circulo_Credito(models.Model):
    # Model Temporal Círculo Crédito
    rfc = models.CharField("RFC", max_length=13, null=True, blank=True)
    tipo_persona = models.CharField("Tipo Persona", max_length=1, null=True, blank=True)
    numero_cuenta = models.CharField("Número Cuenta", max_length=255, null=True, blank=True)
    razon_social = models.CharField("Razón Social", max_length=200, null=True, blank=True)
    nombre = models.CharField("Nombre", max_length=250, null=True, blank=True)
    apellido_paterno = models.CharField("Apellido Paterno", max_length=250, null=True, blank=True)
    apellido_materno = models.CharField("Apellido Materno", max_length=250, null=True, blank=True)
    curp = models.CharField("CURP", max_length=18, null=True, blank=True)
    fecha_nacimiento = models.CharField("Fecha Nacimiento", max_length=20, null=True, blank=True)
    sexo = models.CharField("Sexo", max_length=1, null=True, blank=True)
    nacionalidad = models.CharField("Nacionalidad", max_length=2, null=True, blank=True)
    calle = models.CharField("Calle", max_length=255, null=True, blank=True)
    numero_ext = models.CharField("Numero ext", max_length=30, null=True, blank=True)
    numero_int = models.CharField("Numero int", max_length=30, null=True, blank=True)
    colonia = models.CharField("Colonia", max_length=255, null=True, blank=True)
    municipio = models.CharField("Municipio", max_length=255, null=True, blank=True)
    ciudad = models.CharField("Ciudad", max_length=255, null=True, blank=True)
    estado = models.CharField("Estado", max_length=25, null=True, blank=True)
    cp = models.CharField("Codigo postal", max_length=5, null=True, blank=True)
    telefono = models.CharField("Telefono", max_length=20, null=True, blank=True)
    adeudo = models.DecimalField("Adeudo", max_digits=15, decimal_places=2, null=True, blank=True)
    fecha_alta = models.CharField("Fecha Alta", max_length=20, null=True, blank=True)
    fecha_ultimo_pago = models.CharField("Fecha Ultimo Pago", max_length=20, null=True, blank=True)
    correo = models.CharField("Correo Electrónico", max_length=250, null=True, blank=True)
    interlocutor = models.CharField("Interlocutor", max_length=50, null=True, blank=True)
    objeto_contrato = models.CharField("Objeto Contrato", max_length=50, null=True, blank=True)
    clave = models.CharField("Clave", max_length=4, null=True, blank=True)
    sub_clave = models.CharField("Sub Clave", max_length=4, null=True, blank=True)
    importe_baja = models.DecimalField("Importe Baja", max_digits=15, decimal_places=2, null=True, blank=True)
    periodo = models.CharField("Periodo", max_length=10, null=True, blank=True)
    ejercicio = models.CharField("Ejercicio", max_length=10, null=True, blank=True)
    descripcion = models.CharField("Descripcion", max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "temp_circulo_credito"
        verbose_name_plural = "temp_circulo_creditos"

    def __str__(self):
        return str(self.rfc)


class Historial_Reporte_Circulo_Credito(TimeStampedModel):
    accion = models.CharField("Acción", max_length=500)
    periodo = models.IntegerField("Periodo", default=0)
    ejercicio = models.IntegerField("Ejercicio", default=0)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usuario_historial_cc")

    class Meta:
        verbose_name = "historial_Reporte_Circulo_Credito"
        verbose_name_plural = "historial_Reportes_Circulo_Credito"

    def __str__(self):
        return str(self.accion)

post_save.connect(optimize_image, sender=Contacto)
