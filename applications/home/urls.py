from django.contrib import admin
from django.urls import path
from . import views

app_name = "home_app"

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path('inicio/', views.InicioView.as_view(), name='inicio'),
    path('inicio_new/', views.InicioNewView.as_view(), name='inicio_new'),
    path('home2/', views.InicioAuditoriaView.as_view(), name='home2'),
    path('home3/', views.InicioEjecucionView.as_view(), name='home3'),
    path('home_juridico/', views.InicioJuridicoView.as_view(), name='home_juridico'),

    path('home/', views.Home.as_view(), name='home'),

    path('reporte-ingresos/', views.Reporte_IngresosView.as_view(), name='reporte-ingresos'),
    path('reporte-moac/', views.Reporte_Moac.as_view(), name='reporte-moac'),
    path('reporte-vehicular/', views.Reporte_VehicularView.as_view(), name='reporte-vehicular'),
    path('padron-vehicular/', views.Padron_VehicularView.as_view(), name='padron-vehicular'),
    path('nivel-cumplimiento/', views.Nivel_Cumplimiento.as_view(), name='nivel-cumplimiento'),
    path('recorridos-sectorial/', views.Recorridos_Sectorial.as_view(), name='recorridos-sectorial'),
    path('REC/', views.RECView.as_view(), name='REC'),
    path('organigrama/', views.OrganigramaView.as_view(), name='organigrama'),
    
    path('reporte-vigilancia/', views.Reporte_Vigilancia.as_view(), name='reporte-vigilancia'),
    path('reporte-padrones-fiscales/', views.Reporte_Padrones.as_view(), name='reporte-padrones-fiscales'),


]
