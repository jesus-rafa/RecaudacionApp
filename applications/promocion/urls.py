from django.contrib import admin
from django.urls import path

from . import views

app_name = "promocion_app"

urlpatterns = [
    # urls Actualizaciones
    path(
        'actualizaciones/',
        views.Actualizaciones.as_view(),
        name='actualizaciones'
    ),
    path(
        'actualizaciones/admin/<int:id>/',
        views.Admin_Eventos.as_view(),
        name='actualizaciones-admin'
    ),
    path(
        'actualizaciones/admin/visita/<int:id>/',
        views.Detalle_Visita.as_view(),
        name='detalle-visita'
    ),
    path(
        'ver-tramites/<int:idVisita>/',
        views.Ver_Tramites.as_view(),
        name='ver-tramites'
    ),
    path(
        'todos-tramites/<str:rfc>/',
        views.Todos_Tramites.as_view(),
        name='todos-tramites'
    ),
    path(
        'alta-visita/<int:id>/',
        views.Alta_Visita.as_view(),
        name='alta-visita'
    ),
    path(
        'alta-visita-detalle/<int:idVisita>/<int:idActividad>',
        views.Alta_Detalle.as_view(),
        name='alta-visita-detalle'
    ),
    path(
        'guardar-visita-detalle/<int:idVisita>',
        views.Guardar_Detalle.as_view(),
        name='guardar-visita-detalle'
    ),
    path(
        'editar-visita/<int:pk>/<int:idDesarrollo>/',
        views.Editar_Visita.as_view(),
        name='editar-visita'
    ),
    path(
        'editar-visita-detalle/<int:folio>/<int:idActividad>/',
        views.Editar_Detalle.as_view(),
        name='editar-visita-detalle'
    ),
    path(
        'eliminar-visita/<int:pk>/',
        views.Eliminar_Visita.as_view(),
        name='eliminar-visita'
    ),
    path(
        'eliminar-visita-detalle/<int:folio>/',
        views.Eliminar_Detalle.as_view(),
        name='eliminar-visita-detalle'
    ),
    path(
        'validar-rfc/<int:idDesarrollo>/<str:rfc>/',
        views.Validar_RFC.as_view(),
        name='validar-rfc'
    ),
    path('ver-mercado/<int:id_mercado>', views.Ver_Mercado.as_view(), name='ver-mercado'),

    path('recorridos/', views.Recorridos.as_view(), name='recorridos'),
    path('eventos-promocion/', views.Eventos_Promocion.as_view(), name='eventos-promocion'),
    path('visitas/<int:id_evento>', views.Desarrollos.as_view(), name='visitas'),

    path('programas-promocion/', views.Programas.as_view(), name='programas-promocion'),
    path(
        'crear-programa/',
        views.Alta_Programa.as_view(),
        name='crear-programa'
    ),
    path(
        'crear-evento/',
        views.Alta_Evento.as_view(),
        name='crear-evento'
    ),
    path(
        'crear-desarrollo/',
        views.Alta_Desarrollo.as_view(),
        name='crear-desarrollo'
    ),
    path(
        'modificar-programa/<int:pk>/',
        views.Editar_Programa.as_view(),
        name='modificar-programa'
    ),
    path(
        'ver-programa/<int:pk>/',
        views.Ver_Programa.as_view(),
        name='ver-programa'
    ),
    path(
        'aprobar-programa/<int:pk>/',
        views.Aprobar_Programa.as_view(),
        name='aprobar-programa'
    ),
    path(
        'asignacion-promocion/',
        views.Lista_Promocion.as_view(),
        name='asignacion-promocion'
    ),
]
