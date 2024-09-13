from django.contrib import admin
from django.urls import path
from . import views

app_name = "rec_app"

urlpatterns = [
    path('lista-rec/', views.Lista_Contacto.as_view(), name='lista-rec'),
    path('rec-listado/', views.REC_Listado.as_view(), name='rec-listado'),
    path('cfdi/', views.CFDI.as_view(), name='cfdi'),
    path('ver-cfdi/<int:pk>/', views.Ver_CFDI.as_view(), name='ver-cfdi'),

    path('cartas-invitacion/', views.CartasInvitacion.as_view(), name='cartas-invitacion'),
    path('envio-masivo/', views.EnvioMasivo.as_view(), name='envio-masivo'),
    path('contribuyentes-revisados/', views.ContribuyentesRevisados.as_view(), name='contribuyentes-revisados'),

    path('excel/<str:programa>/', views.DescargarExcel, name='excel'),
    path('excel-masivo/<str:programa>/<str:ejercicio>/<str:periodo>/<str:area>/', views.DescargarExcelMasivo, name='excel-masivo'),
    path('excel-contribuyentes/<str:ejercicio>/<str:periodo>/', views.DescargarExcelContribuyentes, name='excel-contribuyentes'),

    path('lista-rec-2/', views.Lista_Contacto_2.as_view(), name='lista-rec-2'),
    
    path('ver-rec/<int:pk>/', views.Ver_Contacto.as_view(), name='ver-rec'),
    path('alta-rec/<str:rfc>/<int:id>/', views.Alta_Datos.as_view(), name='alta-rec'),
    path('editar-rec/<int:pk>/<int:id>/', views.Editar_Datos.as_view(), name='editar-rec'),
    
    path('resumen-ejecutivo/<str:rfc>/', views.Resumen_Ejecutivo.as_view(), name='resumen-ejecutivo'),
    
    path('eliminar-rec/<int:pk>/', views.Eliminar_Datos.as_view(), name='eliminar-rec'),
    
    path('get-fiscalizados/<rfc>/', views.Get_Fiscalizados.as_view(), name='get-fiscalizados'),
    
    path('registro-civil/', views.Registro_Civil_New.as_view(), name='registro-civil'),

    path(
        'get-contribuyente-name/<rfc>/',
        views.Get_Contribuyente.as_view(),
        name='get-contribuyente-name'
    ),
    # API REC
    path(
        'modal-sintesis/<int:pk>/', 
        views.Modal_Sintesis.as_view(), 
        name='modal-sintesis'
    ),
    path(
        'expediente/', 
        views.Expediente.as_view(), 
        name='expediente'
    ),
    path(
        'api/rec/<str:kword>/',
        views.rec_notificados.as_view(),
    ),
    # API REC
    # CIRCULO CREDITO (inicio)
    path(
        'api/circulo-credito/<str:kword>/',
        views.BusquedaCirculoCredito.as_view(),
    ),
    path(
        'ver-modal/<int:pk>/',
        views.VerModal.as_view(), 
        name='ver-modal'
    ),
    path(
        'circulo-credito/', 
        views.Circulo_Credito_View.as_view(), 
        name='circulo-credito'
    ),
    path(
        'batch-credito/', 
        views.Batch_Credito.as_view(), 
        name='batch-credito'
    ),
    path(
        'excel-credito/<str:archivo>/',
        views.DescargarExcel_Credito, 
        name='excel-credito'
    ),
    path(
        "reporte-circulo-credito/",
        views.ReporteCirculoCreditoView.as_view(),
        name="reporte-circulo-credito"
    ),
    path(
        "descargar-reporte-circulo-credito/",
        views.DescargarExcelReporteCirculo,
        name="descargar-reporte-circulo-credito"
    ),
    path(
        'servicios-contribuyente/',
        views.ServicioContribuyente.as_view(), 
        name='servicios-contribuyente'
    ),
    path(
        'ver-creditos/<str:rfc>/', 
        views.Ver_Creditos.as_view(), 
        name='ver-creditos'
    ),
    # CIRCULO CREDITO (fin)
]
