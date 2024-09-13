from django.contrib import admin
from django.urls import path

from . import views

app_name = 'tramites_app'

urlpatterns = [
    path('tramites-servicios/' ,views.TramitesServiciosView.as_view(), name='tramites-servicios'),
    path('dashboard/', views.ServiciosDashboardView.as_view(), name='dashboard'),
    path('nuevo-tramite/', views.NuevoTramiteView.as_view(), name='nuevo-tramite'),
    path('editar-campo/<int:pk>/', views.EditarCampoView.as_view(), name='editar-campo'),
    path('guardar-estatus',views.GuardarEstatus,name='guardar_estatus'),
    path('vista-individual/<int:pk>', views.VistaIndividualView.as_view(), name='vista-individual'),
    path('activar_vista', views.ActivarVista, name='activar_vista'),
    path('listado-requisitos-tramites/', views.ListadoRequisitosTramites, name='listado-requisitos-tramites'),
    path('guardar-requisitos-tramites/', views.GuardarRequisitosTramites, name='guardar-requisitos-tramites'),
    path('eliminar-requisitos-tramites/', views.EliminarRequisitoTramite, name='eliminar-requisitos-tramites'),
    path('tramite-en-linea/<int:pk>/', views.TramiteEnLineaView.as_view(), name='tramite-en-linea'),
    path('solicitud-tramites/<int:tramite_id>/<str:pk>/<str:action>/', views.SolicitudTramitesView.as_view(), name='solicitud-tramites'),
    path('guardar-requisito-solicitud-tramite/', views.GuardarRequisitoSolicitudTramite, name='guardar-requisito-solicitud-tramite'),
    path('guardar-solicitud-tramite/', views.GuardarSolicitudTramite, name='guardar-solicitud-tramite'),
    path('listado-requisito-solicitud-tramite/', views.ListadoRequisitoSolicitudTramite, name='listado-requisito-solicitud-tramite'),
    path('eliminar-documento-requisito-solicitud/', views.EliminarDocsRequisitoSolicitud, name='eliminar-documento-requisito-solicitud'),
    path('enviar-solicitud-tramite/', views.EnviarSolicitudTramite, name='enviar-solicitud-tramite'),
    path('aceptar-solicitudes-requisitos/', views.AceptarSolicitudesRequisitos, name='aceptar-solicitudes-requisitos'),
    path('autorizacion-solicitudes/', views.AutorizarSolicitudes, name='autorizacion-solicitudes'),
    path('vista-usuarios/',views.VistaUsuario.as_view(),name='usuarios'),
    path('listado-detalles-solicitud/',views.ListadoDetalleSolicitud, name='listado-detalles-solicitud'),
    path('rechazar/<int:pk>',views.RechazarView.as_view(),name='rechazar'),
    path('rechazar_edicion', views.RechazarEdicion, name='rechazar_edicion'),
    path('publicar-view/<int:pk>/',views.PublicarView.as_view(), name='publicar_view'),
    path('vista-publicar',views.PublicarVista,name='vista_publicar'),
    path('observaciones/<int:pk>/',views.ObservacionesView.as_view(),name='observaciones'),
    path('comentarios_detalle',views.ComentariosDetalle,name='comentarios_detalle'),
    path('nueva-prestacion/',views.NuevaPrestacion.as_view(),name='nueva_prestacion'),
    path('editar-nombre/<int:pk>',views.ModalDatos.as_view(),name='editar_nombre'),
    path('eliminar-nuevo-tramite/<int:id>/', views.eliminar_elemento_nuevo_tramite, name='eliminar_nuevo_tramite'),
    path('asignados/<int:pk>',views.AsignarMdal.as_view(),name='asignados'),
    path('solicitudes-por-usuario/',views.TramitesPorUsuario.as_view(),name='solicitudes-por-usuario'),
    path('tomar-nueva-solicitud/',views.TomarNuevaSolicitud, name='tomar-nueva-solicitud'),
    path('validar-solicitud/',views.ValidarSolicitud, name='validar-solicitud'),
]