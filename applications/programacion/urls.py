from django.contrib import admin
from django.urls import path
from . import views
from . import functions

app_name = "programacion_app"

urlpatterns = [
    path('lista-programacion/', views.Lista_Programacion.as_view(), name='lista-programacion'),
    path('seguimiento-vigilancia/', views.Seguimiento_Vigilancia.as_view(), name='seguimiento-vigilancia'),
    path('lista-concluidos/', views.Lista_Concluidos.as_view(), name='lista-concluidos'),
    path('transferencias/', views.Lista_Transferencias.as_view(), name='transferencias'),
    path('admin-programacion/<id>/', views.Admin_Programacion.as_view(), name='admin-programacion'),
    path('ultimos-movimientos/', views.Ultimos_Movimientos.as_view(), name='ultimos-movimientos/'),
    
    path('ver-programacion/<int:pk>/', views.Ver_Programacion.as_view(), name='ver-programacion'),
    path('ver-archivos/<int:pk>/', views.Ver_Archivos.as_view(), name='ver-archivos'),
    path('ver-pagos/<int:pk>/', views.Ver_Pagos.as_view(), name='ver-pagos'),
    
    path('ver-reporte/<int:pk>/', views.Ver_Reporte.as_view(), name='ver-reporte'),
    path('ver-reporte-2/<int:pk>/', views.Ver_Reporte_2.as_view(), name='ver-reporte-2'),
    path('ver-todo/<int:pk>/', views.Ver_Todo.as_view(), name='ver-todo'),
    
    path('alta-programacion/', views.Alta_Programacion.as_view(), name='alta-programacion'),
    
    path('alta-detalle/<int:pk>/', views.Alta_Detalle.as_view(), name='alta-detalle'),
    path('alta-cierre/<int:pk>/', views.Alta_Cierre.as_view(), name='alta-cierre'),
    path('alta-solicitud/<int:pk>/', views.Alta_Solicitud.as_view(), name='alta-solicitud'),
    path('cierre-apoyo/<int:pk>/', views.Cierre_Apoyo.as_view(), name='cierre-apoyo'),
    path('estatus-cierre/<int:pk>/', views.EstatusCierreView.as_view(), name='estatus-cierre'),
    
    path('alta-archivos/<int:pk>/', views.Alta_Archivos.as_view(), name='alta-archivos'),
    path('alta-archivos-ejecucion/<int:pk>/', views.Alta_Archivos2.as_view(), name='alta-archivos-ejecucion'),
    path('alta-archivos-solicitud/<int:pk>/', views.Alta_Archivos_Solicitud.as_view(), name='alta-archivos-solicitud'),

    path('alta-pagos/<int:pk>/', views.Alta_Pagos.as_view(), name='alta-pagos'),

    path('editar-pago/<int:pk>/', views.Editar_Pago.as_view(), name='editar-pago'),
    path('editar-detalle/<int:pk>/', views.Editar_Detalle.as_view(), name='editar-detalle'),
    path('editar-archivo/<int:pk>/', views.Editar_Archivo.as_view(), name='editar-archivo'),
    path('editar-archivo-solicitud/<int:pk>/', views.Editar_Archivo_Solicitud.as_view(), name='editar-archivo-solicitud'),

    path('autorizacion/', views.Lista_Autorizacion.as_view(), name='autorizacion'),
    path('alta-contribuyente/', views.Alta_Contribuyente.as_view(), name='alta-contribuyente'),
    path('elegir/<int:pk>/', views.Elegir_Contribuyente.as_view(), name='elegir'),
    path('impuestos/<int:pk>/', views.ImpuestosView.as_view(), name='impuestos'),

    path('terminar/<int:pk>/', views.Terminar_Contribuyente.as_view(), name='terminar'),
    path('editar-contribuyente/<int:pk>/', views.Editar_Contribuyente.as_view(), name='editar-contribuyente'),
    path('get-contribuyente/<rfc>/', views.Get_Contribuyente.as_view(), name='get-contribuyente'),
    path('ver-autorizacion/<int:pk>/', views.Ver_Autorizacion.as_view(), name='ver-autorizacion'),
    path('asignar/', views.Asignar.as_view(), name='asignar'),
    path('reasignar/', views.Reasignar.as_view(), name='reasignar'),
    
    path('eliminar-archivo/<int:pk>/', views.Eliminar_Archivo.as_view(), name='eliminar-archivo'),
    path('eliminar-detalle/<int:pk>/', views.Eliminar_Detalle.as_view(), name='eliminar-detalle'),
    path('eliminar-pago/<int:pk>/', views.Eliminar_Pagos.as_view(), name='eliminar-pago'),
    
    path('cerrar-rfc/<int:pk>/', views.CerrarRFCView.as_view(), name='cerrar-rfc'),

    path('validar-dato/<str:rfc>/<int:opcion>/', views.Validar_Contribuyente.as_view(), name='validar-dato'),
    path('admin-impuestos/<str:rfc>/<str:impuesto>/', views.Admin_Impuestos.as_view(), name='admin-impuestos'),

    path(
        'subir-archivos-programacion/<int:pk>/', 
        views.Subir_Archivos_Programacion.as_view(), 
        name='subir-archivos-programacion'
    ),
    path(
        'get-files-programacion/<int:pk>/',
        views.Get_Files_Programacion.as_view(),
        name='get-files-programacion'
    ),
    path(
        'eliminar-archivo-programacion/<int:pk>/',
        views.Eliminar_Archivo_Programacion.as_view(),
        name='eliminar-archivo-programacion'
    ),
    path(
        'guardar-archivos-programacion/', 
        views.Guardar_Archivos_Programacion.as_view(), 
        name='guardar-archivos-programacion'
    ),

    path(
        'subir-archivos-vigilancia/<int:pk>/', 
        views.Subir_Archivos_Vigilancia.as_view(), 
        name='subir-archivos-vigilancia'
    ),
    path(
        'get-files-vigilancia/<int:pk>/',
        views.Get_Files_Vigilancia.as_view(),
        name='get-files-vigilancia'
    ),
    path(
        'eliminar-archivo-vigilancia/<int:pk>/',
        views.Eliminar_Archivo_Vigilancia.as_view(),
        name='eliminar-archivo-vigilancia'
    ),
    path(
        'guardar-archivos-vigilancia/', 
        views.Guardar_Archivos_Vigilancia.as_view(), 
        name='guardar-archivos-vigilancia'
    ),
    path(
        'exportar-plan-pagos/', 
        views.ExportarPlanPagos,
        name='exportar-plan-pagos'
    ),
    path(
        'exportar-seguimiento/', 
        views.ExportarSeguimiento,
        name='exportar-seguimiento'
    ),
    path(
        'excel-ultimos-movimientos/', 
        functions.ultimos_movimientos,
        name='excel-ultimos-movimientos'
    ),
    path('contribuyemte/agregar/', views.Agregar_Contribuyente.as_view(), name='add-contribuyente'),    
]
