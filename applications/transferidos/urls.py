from django.contrib import admin
from django.urls import path
from . import views
from . import functions

app_name = "transferidos_app"

urlpatterns = [
    path('lista-transferencias/', views.Lista_Transferencias.as_view(),
         name='lista-transferencias'),
    path('activos-auditoria/', views.Activos_Auditoria.as_view(),
         name='activos-auditoria'),
    path('activos-ejecucion/', views.Activos_Ejecucion.as_view(),
         name='activos-ejecucion'),
    path('admin-transferencias/<str:folio>/', views.Admin_Transferencias.as_view(),
         name='admin-transferencias'),
    path('rechazar/<str:folio>/', views.Rechazar.as_view(),
         name='rechazar'),
    path('aceptar/', views.Aceptar.as_view(),
         name='aceptar'),
    path('opcion/', views.Opcion.as_view(),
         name='opcion'),
    path('lista-auditoria/', views.Lista_Auditoria.as_view(),
         name='lista-auditoria'),
    path('lista-ejecucion/', views.Lista_Ejecucion.as_view(),
         name='lista-ejecucion'),
    path('admin-areas/<str:folio>/', views.Admin_Areas.as_view(),
         name='admin-areas'),
    path('alta-transferencia/', views.Alta_Transferencia.as_view(),
         name="alta-transferencia"),
    path('alta-contribuyente-2/', views.Alta_Contribuyente2.as_view(),
         name='alta-contribuyente-2'),
    path('editar-contribuyente-2/<int:pk>/', views.Editar_Contribuyente.as_view(), name='editar-contribuyente-2'),
    path('consulta-auditoria/', views.Consulta.as_view(), name='consulta-auditoria'),
    path('consulta-ejecucion/', views.Consulta.as_view(), name='consulta-ejecucion'),
    
    
    path('admin-programacion-3/<id>/', views.Admin_Programacion.as_view(), name='admin-programacion-3'),
    path('lista-programacion-auditoria/', views.Lista_Programacion_Auditoria.as_view(), name='lista-programacion-auditoria'),
    path('lista-programacion-ejecucion/', views.Lista_Programacion_Ejecucion.as_view(), name='lista-programacion-ejecucion'),
    path('solicitudes-apoyo/', views.Solicitudes_Apoyo.as_view(), name='solicitudes-apoyo'),
    
    path('ver-reporte-3/<int:pk>/', views.Ver_Reporte.as_view(), name='ver-reporte-3'),
    
    path('alta-detalle-3/<int:pk>/', views.Alta_Detalle.as_view(), name='alta-detalle-3'),    
    path('alta-archivos-3/<int:pk>/', views.Alta_Archivos.as_view(), name='alta-archivos-3'),
    path('alta-pagos-3/<int:pk>/', views.Alta_Pagos.as_view(), name='alta-pagos-3'),
    path('editar-pago-3/<int:pk>/', views.Editar_Pago.as_view(), name='editar-pago-3'),
    path('editar-detalle-3/<int:pk>/', views.Editar_Detalle.as_view(), name='editar-detalle-3'),
    path('editar-archivo-3/<int:pk>/', views.Editar_Archivo.as_view(), name='editar-archivo-3'),
    path('ver-todo-3/<int:pk>/', views.Ver_Todo.as_view(), name='ver-todo-3'),
    path('eliminar-detalle-3/<int:pk>/', views.Eliminar_Detalle.as_view(), name='eliminar-detalle-3'),
    path('eliminar-pago-3/<int:pk>/', views.Eliminar_Pagos.as_view(), name='eliminar-pago-3'),
    path('eliminar-archivo-3/<int:pk>/', views.Eliminar_Archivos.as_view(), name='eliminar-archivo-3'),
    path('get-contribuyente-2/<rfc>/', views.Get_Contribuyente2.as_view(), name='get-contribuyente-2'),
    
    path('get-data/<rfc>/', views.Get_Data.as_view(), name='get-data'),
    path('get-no-control/<rfc>/', views.Get_NoControl.as_view(), name='get-no-control'),

    
    path('aceptar-todos/', views.Aceptar_Todos.as_view(),
         name='aceptar-todos'),
    path('rechazar-todos/', views.Rechazar_Todos.as_view(),
         name='rechazar-todos'),
    path('asignar-auditoria/', views.Asignar_Auditoria.as_view(), name='asignar-auditoria'),
    path('asignar-solicitud/', views.Asignar_Solicitud.as_view(), name='asignar-solicitud'),

    path('alta-ejecucion/', views.Alta_Ejecucion.as_view(), name='alta-ejecucion'),
    path('editar-ejecucion/<int:pk>/', views.Editar_Ejecucion.as_view(), name='editar-ejecucion'),
    
    path('concluidos-ejecucion/', views.Concluidos_Ejecucion.as_view(), name='concluidos-ejecucion'),
    path('seguimiento-ejecucion/', views.Seguimiento_Ejecucion.as_view(), name='seguimiento-ejecucion'),

    path('concluidos-auditoria/', views.Concluidos_Auditoria.as_view(), name='concluidos-auditoria'),
    path('seguimiento-auditoria/', views.Seguimiento_Auditoria.as_view(), name='seguimiento-auditoria'),
    path('fecha-cierre/<int:pk>/', views.Fecha_Cierre.as_view(), name='fecha-cierre'),

    path('batch/', views.Batch_Ejecucion.as_view(), name='batch'),
    path('excel-ejecucion/<str:archivo>/', views.DescargarExcel, name='excel-ejecucion'),
    path('excel-activos-auditoria/', functions.activos_auditoria, name='excel-activos-auditoria'),
    path('excel-activos-ejecucion/', functions.activos_ejecucion, name='excel-activos-auditoria'),

    path('impuestos-transferidos/<int:pk>/', views.ImpuestosView.as_view(), name='impuestos-transferidos'),
    path('limpiar-impuestos/', views.LimpiarImpuestos.as_view(), name='limpiar-impuestos'),
    path('ver-impuestos-transferidos/<int:rfc>/', views.Ver_Impuestos.as_view(), name='ver-impuestos-transferidos'),

    path('admin-impuestos-transferidos/<str:rfc>/<str:impuesto>/', views.Admin_Impuestos.as_view(), name='admin-impuestos-transferidos'),
]
