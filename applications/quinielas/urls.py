from django.contrib import admin
from django.urls import path

from . import views

app_name = "quinielas_app"

urlpatterns = [
    # urls Actualizaciones
   
    # path(
    #     'asignacion-promocion/',
    #     views.Lista_Promocion.as_view(),
    #     name='asignacion-promocion'
    # ),

    path('pronostico/', views.Pronostico_View.as_view(), name='pronostico'),
    path('crea-pronostico/',views.Crea_Pronostico,name='crea-pronostico'),
    path('edita-pronostico/',views.Edita_Pronostico,name='edita-pronostico'),
    path('resultados_pronosticos/', views.ReportePronosticos.as_view(), name='resultados_pronosticos'),
    path('tabulador-quiniela/', views.Tabulador_Quiniela_View.as_view(), name='tabulador-quiniela')
]
