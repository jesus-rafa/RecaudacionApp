from django.contrib import admin
from django.urls import path

from . import views


app_name = 'verificacion_app'

urlpatterns = [
    path('verificacion-vehicular/<str:no_serie>/',views.VerificacionVehicular.as_view(),name='verificacion-vehicular'),
    path('exportar-historial-busquedas-verif/<str:no_serie>/',views.ExportarHistorialBusquedasVerif,name='exportar-historial-busquedas-verif')
]