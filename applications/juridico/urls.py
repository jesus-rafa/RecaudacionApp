from django.urls import path

from . import views

app_name = "juridico_app"

urlpatterns = [
    path('juridico/', views.Demanda_View.as_view(), name='juridico'),
    #     path('creacion/', views.panelJuridico.as_view(), name='panel-juridico'),
    path('alta-demanda/', views.Alta_Demanda.as_view(), name='alta-demanda'),
    path('edita-demanda/<int:pk>/', views.Edita_Demanda.as_view(), name='edita-demanda'),
    # path('alta-demanda/#profile1', views.Alta_Demanda.as_view(), name='alta-demanda'),
    # path('alta-detalle/', views.Alta_Detalle.as_view(), name='alta-detalle'),
    path('demanda/<int:id>/', views.Detalle_Demanda.as_view(),
         name='detalle-demanda'),
    path('ver-demanda/<int:pk>/',
         views.Ver_Detalle_Demanda.as_view(), name='ver-demanda'),
    path('plantilla/<str:id_juicio>/<str:id_subtipo>/<str:fecha_notificacion>/<str:fecha_aviso>/',
         views.PlantillaView.as_view(), name='plantilla'),
    path('plantilla/<str:id_juicio>/<str:id_subtipo>/<str:fecha_notificacion>/',
         views.PlantillaView.as_view(), name='plantilla'),
    path('home_Juridico/', views.InicioEjecucionView.as_view(), name='home_Juridico'),

    # Administart Demanda
    path(
        'admin-demanda/<int:pk>/',
        views.Admin_Demanda.as_view(),
        name='admin-demanda'
    ),
    path(
        'alta-proceso/<int:formulario_id>/<int:demanda>/<int:padre>/<int:rubro>',
        views.Alta_Formulario.as_view(),
        name='alta-proceso'
    ),
    path(
        'subir-archivos-juridico/<int:pk>/',
        views.Subir_Archivos.as_view(),
        name='subir-archivos-juridico'
    ),
    path(
        'get-files-juridico/<int:pk>/',
        views.Get_Files.as_view(),
        name='get-files-juridico'
    ),
    path(
        'eliminar-archivo-juridico/<int:pk>/',
        views.Eliminar_Archivo.as_view(),
        name='eliminar-archivo-juridico'
    ),
    path(
    'ver-detalle-proceso/<int:proceso>/<int:formulario>/',
    views.Ver_Detalle_Proceso.as_view(),
    name='ver-detalle-proceso'
    ),
    path(
    'actualiza-detalle-proceso/<int:proceso>/<int:formulario>/',
    views.Actualiza_Detalle_Proceso.as_view(),
    name='actualiza-detalle-proceso'
    ),
    path(
    'elimina-demanda/<int:pk>/',
    views.Elimina_Demanda.as_view(),
    name='elimina-demanda'
    ),
    path(
    'computo-proceso/<str:proceso>/<str:notificacion>/',
    views.Computo_Proceso.as_view(),
    name='computo-proceso'
    ),
    path(
    'elimina-proceso/',
    views.Elimina_Proceso,
    name='elimina-proceso'
    ),
    path(
    'expediente-modal/',
    views.Expediente.as_view(),
    name='expediente-modal'
    ),
    path('demanda/json/', views.demanda_json, name='demanda_json'),
    path('demanda-page/', views.demanda_page, name='demanda_page'),

    #"""RESOLUTOR"""
        #"""CAPTURA"""
    path('juridico/resolutor/solicitante', views.Solicitantes.as_view(), name='alta_solicitante'),
    path('juridico/resolutor/solicitante/<int:pk>/', views.SolicitanteActualiza.as_view(), name='actualiza_solicitante'),
    path('juridico/resolutor/alta', views.Resolutores.as_view(), name='alta_resolutor'),
    path('juridico/resolutor/actualiza/<int:pk>/', views.ResolutorActualiza.as_view(), name='actualiza_resolutor'),
    path('juridico/getSolicitante/<str:kword>/', views.resolutor_solicitante.as_view(), name='getSolicitante'),
    path('juridico/getSolicitanteId/<int:kword>/', views.resolutor_solicitanteId.as_view(), name='getSolicitanteId'),
    path('juridico/solicitanteActivo/', views.BuscarSolicitante, name='solicitanteActivo'),
        #"""PANEL"""
    path('juridico/resolutor', views.PanelResolutorView.as_view(), name='panel-resolutor'),
    path('asignar-abogados/', views.AsignarAbogados, name='asignar-abogados'),
    path('buscar-abogados-asignados/', views.BuscarAbogadosAsignados, name='buscar-abogados-asignados'),   
        #"""DETALLE"""
    path('juridico/resolutor/detalle/<int:pk>/', views.Ver_detalle_resolutor.as_view(), name='resolutor-detalle'),
    path('juridico/resolutor/detalle/elimina/<int:pk>/', views.Elimina_detalle.as_view(), name='detalle-eliminar'),
    path('juridico/resolutor/detalle/agregar/', views.AgregarDetalle, name='detalle-agregar'),
    path('juridico/resolutor/detalle/agregar/archivo/<int:pk>/<int:fk>/', views.Resolutor_AltaArchivo.as_view(), name='resolutorArchivo-alta'),
    path('juridico/resolutor/detalle/agregar/archivo/ejecucion/<int:pk>/<int:fk>/', views.Resolutor_AltaArchivo.as_view(), name='resolutorArchivo-alta'),
    path('juridico/resolutor/detalle/requisito/abogado/<int:pk>/', views.Resolutor_detalleList.as_view(), name='resolutorDetalle'),
    path('juridico/resolutor/detalle/requisito/ejecutor/<int:pk>/', views.Resolutor_ejecucion.as_view(), name='resolutorEjecucion'),
    path('juridico/resolutor/lectura/<int:pk>/', views.Resolutor_lectura.as_view(), name='resolutorLectura'),
        #"""REQUISITOS"""
    path('juridico/resolutor/revision/<int:pk>/', views.Resolutor_Revision.as_view(), name='resolutorRevision'),
    path('juridico/resolutor/aceptar/<int:pk>/', views.Resolutor_Aceptar, name='resolutorAceptar'),
    path('juridico/resolutor/rechazar/<int:pk>/', views.Resolutor_Rechazar, name='resolutorRechazar'),
    path('juridico/resolutor/requisito/alta/<int:pk>/', views.Resolutor_AltaRequisito.as_view(), name='resolutorRequisito-alta'),
    path('juridico/resolutor/requisito/actualiza/<int:pk>/', views.Resolutor_ActualizaRequisito.as_view(), name='resolutorRequisito-actualiza'),
    path('juridico/resolutor/requisito/elimina/<int:pk>/', views.Resolutor_EliminaRequisito, name='resolutorRequisito-elimina'),
        #"""REPORTERIA Y FIRMA"""
    path('generate/refrendo/<int:pk>/', views.generatePdfRefrendo, name='resolutorRefrendo'),
    path('generate/tenencia/<int:pk>/', views.generatePdfTenencia, name='resolutorTenencia'),
    path('generate/refrendo/tenencia/<int:pk>/', views.generatePdfRefrendoTenencia, name='resolutorgeneratePdfRefrendoTenencia'),
    path('juridico/resolutor/firma/<int:pk>/', views.Resolutor_Firma, name='resolutorFirma'),
    path('juridico/resolutor/reportes/<int:pk>/', views.Resolutor_AltaReporte.as_view(), name='cargaReportes'),
    path('juridico/resolutor/concluir/manual/<int:pk>/', views.ConcluirManual, name='concluirManual'),








    
]
