from django.contrib import admin
from django.urls import path
from . import functions
from . import views

app_name = "direccion_app"

urlpatterns = [
    path('direccion/', views.Direccion.as_view(), name='direccion'),
    path(
        'excel-informativas/', 
        functions.informativas,
        name='excel-informativas'
    ),
    path(
        'excel-fiscalizados/', 
        functions.fiscalizados,
        name='excel-fiscalizados'
    ),
]