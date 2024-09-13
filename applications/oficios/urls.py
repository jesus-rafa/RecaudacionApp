from django.contrib import admin
from django.urls import path

from . import views

app_name = "oficios_app"

urlpatterns = [
    path('lista-oficios/<item>/',
         views.Lista_Oficios.as_view(), name='lista-oficios'),
    path('alta-oficios/', views.Alta_Oficios.as_view(), name="alta-oficios"),
    path('editar-oficios/<int:pk>/',
         views.Editar_Oficios.as_view(), name="editar-oficios"),
    path('lista-oficios-recibidos/<item>/',
         views.Lista_Recibidos.as_view(), name="lista-oficios-recibidos"),
    path('alta-recibidos/', views.Alta_Recibidos.as_view(), name="alta-recibidos"),
    path('editar-recibidos/<int:pk>/',
         views.Editar_Recibidos.as_view(), name="editar-recibidos"),

    path('alta-permisos/<int:pk>',
         views.CrearPermisosView.as_view(), name="alta-permisos"),
    path('alta-compartidos/<int:pk>',
         views.CrearCompartidosView.as_view(), name="alta-compartidos"),
    path('control-oficios/', views.Control_Oficios.as_view(), name="control-oficios"),
    path('correspondencia/<item>/',
         views.CorrespondenciaView.as_view(), name="correspondencia"),

    path('panel/<item>/<int:vista>', views.Correspondencia.as_view(), name="panel"),

    path('recibir-oficio/', views.Recibir_Oficio.as_view(), name='recibir-oficio'),
    path(
        'subir-archivos/<int:option>/<int:pk>/',
        views.Subir_Archivos.as_view(),
        name='subir-archivos'
    ),
    path(
        'get-files/<int:option>/<int:pk>/',
        views.Get_Files.as_view(),
        name='get-files'
    ),
    path(
        'eliminar-archivo/<int:option>/<int:pk>/',
        views.Eliminar_Archivo.as_view(),
        name='eliminar-archivo'
    ),

    path('editar-oficio-recibido/<int:pk>/',
         views.Editar_Oficio_Recibido.as_view(), name="editar-oficio-recibido"),
    path('visto/<int:id_oficio>/<int:id_user>/<str:tipo>/',
         views.Visto.as_view(), name='visto'),
    path('visto-oficio/<int:id_oficio>/<int:id_user>/',
         views.Visto_Oficio.as_view(), name='visto-oficio'),
    path('ver-oficios-recibidos/<int:pk>/',
         views.Ver_Recibidos.as_view(), name="ver-oficios-recibidos"),

    path('nuevo-oficio/', views.Nuevo_Oficio.as_view(), name='nuevo-oficio'),
    path('modificar-oficio/<int:pk>/',
         views.Modificar_Oficio.as_view(), name="modificar-oficio"),
    path('ver-oficios/<int:pk>/', views.Ver_Oficios.as_view(), name="ver-oficios"),

    path('cerrar-oficio/<int:pk>/',
         views.Cerrar_Oficio.as_view(), name='cerrar-oficio'),
    path('cerrar-oficio-recibido/<int:pk>/',
         views.Cerrar_Oficio_Recibido.as_view(), name='cerrar-oficio-recibido'),

    path('contestar-oficio-recibido/<int:pk>/',
         views.Contestar_Oficio_Recibido.as_view(), name='contestar-oficio-recibido'),

    path('cerrar-recibido/<int:pk>/',
         views.Cerrar_Recibido.as_view(), name='cerrar-recibido'),

    path('turnar-oficio/<int:pk>/', views.Turnar.as_view(), name='turnar-oficio'),

    path('cmmt-oficio/<int:id_oficio>/<int:id_user>/',
         views.Cmmt_Oficio.as_view(), name='cmmt-oficio'),
    path('cmmt-recibido/<int:id_oficio>/<int:id_user>/',
         views.Cmmt_Recibido.as_view(), name='cmmt-recibido'),
    path('declinar-recibido/<int:id_oficio>/<int:id_user>/',
         views.Declinar_Recibido.as_view(), name='declinar-recibido'),
]
