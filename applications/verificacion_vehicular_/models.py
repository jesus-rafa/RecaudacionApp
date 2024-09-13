from django.conf import settings
from django.db import models
from applications.users.models import User, Areas
from model_utils.models import TimeStampedModel


class Vehiculo(TimeStampedModel):
    serie = models.CharField("Descripción", max_length=255)

    class Meta:
        verbose_name = "Vehiculo"
        verbose_name_plural = "Vehiculos"
    
    def __str__(self):
        return self.nombre


class Historial_Busqueda(TimeStampedModel):
    busqueda = models.CharField("Búsqueda realizada", max_length=600)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hitorial_busqueda_usuario")

    class Meta:
        verbose_name = "Historial de búsqueda"
        verbose_name_plural = "Historial de búsquedas"
    
    def __str__(self):
        return self.busqueda
