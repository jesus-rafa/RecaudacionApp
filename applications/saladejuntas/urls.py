from django.contrib import admin
from django.urls import path
from . import views

app_name = "sala_app"

urlpatterns = [
    path('salajuntas/',views.SalasJuntasView.as_view(), name='salajuntas'),
    path('salageneral/',views.SalaVistaGeneral.as_view(), name='salageneral'),
    path('consulta-reuniones/',views.ConsultaReunionesBySala, name='consulta-reuniones'),
    path('crear-reuniones/',views.Crear_Reunion, name='crear-reuniones'),
    path('buscar-reuniones/',views.BuscarReuniones, name='buscar-reuniones'),
    path('eliminar-reuniones/',views.EliminarReuniones, name='eliminar-reuniones'),
    path('buscar-salas',views.BuscarSalas,name='buscar-salas'),
    path('descargarListadoAsist-reuniones/<str:reunion>/', views.ListaAsistenciaReuniones, name='descargarListadoAsist-reuniones'),
    path('buscar-salas_disponibles/', views.BuscarSalasDisponibles, name='buscar-salas_disponibles'),
    path('buscar-info-sala/', views.BuscarInformacionSala, name='buscar-info-sala'),
    path('actualizar-info-sala/', views.ActualizarInfoSala, name='actualizar-info-sala'),
    path('buscar-correo-notificacion/', views.BuscarCorreoNotificacion, name='buscar-correo-notificacion'),
    path('ordenar-salas',views.OrdenarSala, name='ordenar_salas'),
    path('activar-desactivar-sala/', views.ActivarDesactivarSalas, name='activar-desactivar-sala'),
    path('buscar-correo-usuario',views.BuscarCorreoUsuario, name='buscar-correo-usuario'),
]