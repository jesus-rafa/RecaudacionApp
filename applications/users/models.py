from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django.conf import settings


class Areas(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    clave = models.CharField('Clave', max_length=100, blank=True, null=True)
    area = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE, related_name="areas"
    )
    correo_notificacion_coffe_break = models.CharField("Correo Notificación Coffe Break", max_length=1000, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Areas'
        verbose_name_plural = 'Areas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class User(AbstractBaseUser, PermissionsMixin):
    """ Model Users """

    username = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    nombres = models.CharField(max_length=50, blank=True)
    apellidos = models.CharField(max_length=50, blank=True)
    area = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.FileField('Avatar', upload_to='users', blank=True, null=True)
    telefono = models.CharField('Telefono', max_length=10, blank=True, null=True)
    ext = models.CharField('Ext', max_length=5, blank=True, null=True)
    jefe_directo = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE, related_name="jerarquia"
    )
    areas = models.ForeignKey(Areas, blank=True, null=True, on_delete=models.CASCADE, related_name='user_area')
    unidad = models.ForeignKey(Areas, blank=True, null=True, on_delete=models.CASCADE, related_name='user_unidad')
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres','apellidos',]
    
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.username = self.email.split('@')[0]
        super(User, self).save(*args, **kwargs)

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return self.nombres + ' ' + self.apellidos
        
    def get_initials(self):
        return self.nombres[:1].upper() + self.apellidos[:1].upper()
    
    def get_user(self):
        return self.nombres + ' ' + self.apellidos + ' (' + self.username + ')'
    
    def __str__(self):
        return self.nombres + ' ' + self.apellidos + ' (' + self.username + ')'


class Plantilla(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plantilla')
    orientacion = models.IntegerField('Orientacion', default=0)
    barra = models.IntegerField('Barra', default=0)
    menu = models.IntegerField('Menu', default=0)

    class Meta:
        verbose_name = 'Plantilla'
        verbose_name_plural = 'Plantilla'
        ordering = ['user']

    def __str__(self):
        return str(self.user)
        
        
class Urls(models.Model):
    url = models.CharField('Urls', max_length=100)
    icono = models.CharField('Icono', max_length=100, blank=True, null=True)
    nombre = models.CharField('Nombre', max_length=100, blank=True, null=True)
    tags = models.CharField('Tags', max_length=200, blank=True, null=True)
    #padre = models.CharField('Padre', max_length=100, blank=True, null=True)
    padre = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE, related_name="hijos"
    )
    sort = models.IntegerField('Sort', blank=True, null=True)
    nivel = models.IntegerField('Nivel', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Urls'
        verbose_name_plural = 'Urls'
        ordering = ['sort']

    def __str__(self):
        return self.nombre

     



class Accesos(models.Model):
    perfil = models.ForeignKey(Group, on_delete=models.CASCADE)
    urls = models.ManyToManyField(Urls, blank=True, related_name='get_urls')

    class Meta:
        verbose_name = 'Accesos'
        verbose_name_plural = 'Accesos'
        ordering = ['perfil']

    def __str__(self):
        return str(self.perfil)