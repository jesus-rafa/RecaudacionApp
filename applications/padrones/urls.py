from django.contrib import admin
from django.urls import path
from . import views
from . import functions

app_name = "padrones_app"

urlpatterns = [
    path('lista-programacion-2/', views.Lista_Programacion.as_view(), name='lista-programacion-2'),
    path('lista-programacion-padrones/', views.Lista_Programacion_Padrones.as_view(), name='lista-programacion-padrones'),
    path('programas-especiales/', views.Programas_Especiales.as_view(), name='programas-especiales'),
    path('reporte-padrones/', views.Reporte_Padrones.as_view(), name='reporte-padrones'),
    path('reporte-detalle/<str:folio>/', views.Reporte_Detalle.as_view(), name='reporte-detalle'),
         
    path('admin-programacion-2/<id>/', views.Admin_Programacion.as_view(), name='admin-programacion-2'),
    
    path('ver-programacion-2/<int:pk>/', views.Ver_Programacion.as_view(), name='ver-programacion-2'),
    path('ver-archivos-2/<int:pk>/', views.Ver_Archivos.as_view(), name='ver-archivos-2'),
    path('ver-pagos-2/<int:pk>/', views.Ver_Pagos.as_view(), name='ver-pagos-2'),

    path('alta-programacion-2/', views.Alta_Programacion.as_view(), name='alta-programacion-2'),
    path('alta-detalle-2/<int:pk>/', views.Alta_Detalle.as_view(), name='alta-detalle-2'),
    path('alta-archivos-2/<int:pk>/', views.Alta_Archivos.as_view(), name='alta-archivos-2'),
    path('alta-pagos-2/<int:pk>/', views.Alta_Pagos.as_view(), name='alta-pagos-2'),

    path('turnar/', views.Turnar_Programacion.as_view(), name='turnar'),
    
    path('editar-pago-2/<int:pk>/', views.Editar_Pago.as_view(), name='editar-pago-2'),
    path('editar-detalle-2/<int:pk>/', views.Editar_Detalle.as_view(), name='editar-detalle-2'),
    path('editar-archivo-2/<int:pk>/', views.Editar_Archivo.as_view(), name='editar-archivo-2'),
    
    path('eliminar-archivo-2/<int:pk>/', views.Eliminar_Archivo.as_view(), name='eliminar-archivo-2'),
    path('eliminar-detalle-2/<int:pk>/', views.Eliminar_Detalle.as_view(), name='eliminar-detalle-2'),
    path('eliminar-pago-2/<int:pk>/', views.Eliminar_Pagos.as_view(), name='eliminar-pago-2'),
    path('excel-padrones/', functions.padrones, name='excel-padrones'),
    path('envio-insumos/', views.EnvioInsumoView.as_view(), name='envio-insumos'),
    path('carga-programa-padrones-masivo/', views.GuardarMasivoProgramasPadrones, name='carga-programa-padrones-masivo'),
]