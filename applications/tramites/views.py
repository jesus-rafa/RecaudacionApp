import json
import random
import pytz
from os import remove
from datetime import datetime, date

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView)
from django.db.models import Q, Sum, F, Case, Count, When
from django.shortcuts import render

from .models import NuevoTramite, Tipos, Estatus, Requisitos, Solicitud, Detalle_solicitud_temporal, Estatus_Solicitud, Detalle_Solicitud, Historial_Solicitudes, Observaciones
from applications.users.models import User
from applications.tramites.forms import (FormNuevoTramite)


class TramitesServiciosView(LoginRequiredMixin,ListView):
    template_name = 'tramites/tramites-servicios.html'
    context_object_name = 'servicios' 

    def get_queryset(self):
        servicio = NuevoTramite.objects.all()
     
        return servicio
    
    def get_context_data(self, **kwargs):
        context = super(TramitesServiciosView, self).get_context_data(**kwargs)  

        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='TRAMITES ADMINISTRADOR'):
            context['permission'] = 'TRAMITES ADMINISTRADOR'
        elif User.objects.filter(username=user, groups__name__contains='TRAMITES EDITOR'):
            context['permission'] = 'TRAMITES EDITOR'                

        context['tramites'] = NuevoTramite.objects.all()
        context["tramites_servicios"] = NuevoTramite.objects.exclude(estatus=4)
        context["estatus_tramite"] = Estatus_Solicitud.objects.all() 

        return context

def ListadoRequisitosTramites(request):
    FormData = request.POST

    listado_requisitos = Requisitos.objects.filter(tramite=FormData["tramite_id"]).values("id", "nombre", "obligatorio", "tiene_formato_default", "ruta_formato", "ruta_nombre_archivo")

    return JsonResponse({'data': list(listado_requisitos) })

def GuardarRequisitosTramites(request):
    FormData = request.POST
    FileData = request.FILES

    nombre_archivo = ""
    path = ""
    
    tramites_instance = NuevoTramite.objects.get(pk=FormData["id_tramite"])

    if FormData["tramites_Requisitos-id"]:
        requisitos_instance = Requisitos.objects.get(pk=FormData["tramites_Requisitos-id"])
        if requisitos_instance.ruta_formato:
            a_ruta = str(requisitos_instance.ruta_formato).split('/')
            path_ant = settings.MEDIA_ROOT + '/tramites/' + a_ruta[2]

            # Eliminamos el documento conforme a la ruta guardada
            remove(path_ant)

    if "tramites_Requisitos-ruta_nombre_archivo" in FileData:
        if FileData["tramites_Requisitos-ruta_nombre_archivo"]:
            nombre_archivo = FileData["tramites_Requisitos-ruta_nombre_archivo"].name
            a_nombre_archivo = str(nombre_archivo).split('.')
            archivo = FileData["tramites_Requisitos-ruta_nombre_archivo"]

            tramite = str(FormData["id_tramite"]).rjust(6, '0')
            today = datetime.now()
            format_today =  today.strftime("%d%m%Y_%H%M%S")
            random_number = str(random.randint(0, 1000))

            rename_file = tramite + format_today + random_number + '.' + a_nombre_archivo[1]

            path = settings.MEDIA_ROOT + '/tramites/' + rename_file

            with open(path, 'wb') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)   

    obligatorio = False
    if "tramites_Requisitos-obligatorio" in FormData:
        if FormData["tramites_Requisitos-obligatorio"] == 'on':
            obligatorio = True

    tiene_formato_defecto = False
    if "tramites_Requisitos-tiene_formato_default" in FormData:
        if FormData["tramites_Requisitos-tiene_formato_default"] == 'on':
            tiene_formato_defecto = True

    if FormData["tramites_Requisitos-id"]:
        requisitos_instance = Requisitos.objects.get(pk=FormData["tramites_Requisitos-id"])
        requisitos_instance.nombre = FormData["tramites_Requisitos-nombre"]
        requisitos_instance.obligatorio = obligatorio
        requisitos_instance.tiene_formato_default = tiene_formato_defecto
        requisitos_instance.ruta_formato = path
        requisitos_instance.ruta_nombre_archivo = nombre_archivo
        requisitos_instance.save()
    else:
        Requisitos.objects.create(
            nombre=FormData["tramites_Requisitos-nombre"],
            obligatorio=obligatorio,
            tiene_formato_default=tiene_formato_defecto,
            ruta_formato=path,
            ruta_nombre_archivo=nombre_archivo,
            tramite=tramites_instance,
        ).save()

    return JsonResponse({'error': False, 'msj': "Datos guardados correctamente" })

def EliminarRequisitoTramite(request):
    FormData = request.POST

    if FormData["ruta"]:
        a_ruta = FormData["ruta"].split('/')
        path = settings.MEDIA_ROOT + '/tramites/' + a_ruta[2]

        # Eliminamos el documento conforme a la ruta guardada
        remove(path)

    # Eliminamos el registro del documento guardado
    requisitos_instance = Requisitos.objects.get(pk=FormData["requisito_id"])
    requisitos_instance.delete()
    
    return JsonResponse({'error': False, 'msj': "Requisito eliminado correctamente" })

def ActivarVista(request):           

    FormData = request.POST   

    activar_instance = NuevoTramite.objects.get(pk=FormData['activar'])
    catalogo_estatus_instance = Estatus.objects.get(esta_tus=FormData['estatus'])
    activar_instance.estatus = catalogo_estatus_instance
    activar_instance.save()

    return JsonResponse({'error': False, 'msj': "Documento en proceso" })

def eliminar_elemento_nuevo_tramite(request, id):          
    elemento = NuevoTramite.objects.get(id=id)       
    elemento.delete()
    return redirect('tramites_app:tramites-servicios')   

class NuevoTramiteView(LoginRequiredMixin , SuccessMessageMixin ,CreateView):
    Model = NuevoTramite
    template_name = 'tramites/nuevo-tramite.html'
    form_class = FormNuevoTramite

    def get_success_url(self):
        messages.success(self.request, 'se guardo con exito')
        return reverse_lazy('tramites_app:tramites-servicios')


class ServiciosDashboardView(ListView):
    template_name = 'tramites/tramites-dashboard.html'
    context_object_name = 'dashboard'

    def get_queryset(self):
        dash = NuevoTramite.objects.all()

        return dash       


class EditarCampoView(UpdateView): 
    queryset = NuevoTramite.objects.all()         
    template_name = 'tramites/editar-tramite.html'                
    form_class = FormNuevoTramite 

    def get_context_data(self, **kwargs):   
        context = super(EditarCampoView, self).get_context_data(**kwargs)      
        idvista = self.kwargs.get('pk')       

        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='TRAMITES ADMINISTRADOR'):
            context['permission'] = 'TRAMITES ADMINISTRADOR'
        elif User.objects.filter(username=user, groups__name__contains='TRAMITES EDITOR'):
            context['permission'] = 'TRAMITES EDITOR'
        
        context['verEditar'] = NuevoTramite.objects.filter(id=idvista)        
        
        context['activar_vista'] = NuevoTramite.objects.all() 

        context['tablaVista'] = Observaciones.objects.filter(is_active=True,tramite=idvista).order_by('detalle')  

        return context 

    # def form_valid(self, form):
    #     form.instance.estatus = Estatus.objects.get(esta_tus='Revisión')    
       

    #     return super(EditarCampoView, self).form_valid(form)  

    def get_success_url(self):
        messages.success(self.request, 'se guardo con exito')        
        return reverse_lazy('tramites_app:tramites-servicios')
    
def GuardarEstatus(request):   

    FormData = request.POST              

    activar_instance = NuevoTramite.objects.get(pk=FormData['activar'])
    catalogo_estatus_instance = Estatus.objects.get(esta_tus=FormData['estatus'])   
    activar_instance.estatus = catalogo_estatus_instance
    activar_instance.save()

    return JsonResponse({'error': False, 'msj': "Documento en proceso" })


class VistaIndividualView(UpdateView):    
    queryset = NuevoTramite.objects.all()
    template_name  = 'tramites/ver-individual.html'
    form_class = FormNuevoTramite

    def get_context_data(self, **kwargs):
        context = super(VistaIndividualView, self).get_context_data(**kwargs)
        
        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='TRAMITES ADMINISTRADOR'):
            context['permission'] = 'TRAMITES ADMINISTRADOR'
        elif User.objects.filter(username=user, groups__name__contains='TRAMITES EDITOR'):
            context['permission'] = 'TRAMITES EDITOR'              
        
        tramite_id = self.kwargs.get('pk')

        context["tramite"] = tramite_id
        context['verindividual'] = NuevoTramite.objects.filter(id=tramite_id)   

        return context

    def get_success_url(self):  
        messages.success(self.request, 'se guardo con exito')
        return reverse_lazy('tramites_app:tramites-servicios')  


class TramitesPorUsuario(LoginRequiredMixin, ListView):
    template_name = "tramites/tramite_en_linea/administrar-tramites-propios.html"
    context_object_name = "tramites_activos"

    def get_queryset(self):
        queryset = Solicitud.objects.filter(usuario=self.request.user.id).exclude(estatus=7).order_by("-created")

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TramitesPorUsuario, self).get_context_data(**kwargs)

        context["tramites_concluidos"] = Solicitud.objects.filter(usuario=self.request.user.id, estatus=7).order_by("-created")

        return context


class TramiteEnLineaView(LoginRequiredMixin, ListView):
    template_name = 'tramites/tramite_en_linea/tramite-en-linea.html'
    context_object_name = "tramites_en_linea"

    def get_queryset(self):
        tramite_id = self.kwargs.get('pk')
        queryset = Solicitud.objects.filter(tramite=tramite_id, usuario=self.request.user.id).order_by("-estatus")

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TramiteEnLineaView, self).get_context_data(**kwargs)
        tramite_id = self.kwargs.get('pk')

        context['perfil_usuario'] = "TRAMITES USUARIO"
        if User.objects.filter(username=self.request.user.username, groups__name__in=['TRAMITES ADMINISTRADOR']).exists():
            context['perfil_usuario'] = "TRAMITES ADMINISTRADOR"

        context['permite_nueva_solicitud'] = True
        historial_solicitudes_usuario = Solicitud.objects.filter(tramite=tramite_id, usuario=self.request.user.id, estatus__nombre__in=["ENVIADA", "ACEPTADA", "GUARDADA", "RECHAZADA"])
        if historial_solicitudes_usuario:
            context['permite_nueva_solicitud'] = False

        context['solicitudes_tramite'] = Solicitud.objects.filter(Q(tramite=tramite_id) & Q(estatus__nombre__in=["ENVIADA", "ACEPTADA", "AUTORIZADA"]) & ~Q(usuario=self.request.user.id)).order_by("-fecha_inicio")
        context['tramite_id'] = tramite_id
        context["tramite"] = NuevoTramite.objects.get(pk=tramite_id)
        context["user_login"] = self.request.user.username
        
        context["solicitudes_pendientes"] = Solicitud.objects.filter(usuario_asignado=self.request.user.id, tramite=tramite_id).exclude(estatus__nombre__in=["AUTORIZADA", "GUARDADA", "ENVIADA"]).order_by("-fecha_inicio")
        context["solicitudes_enviadas"] = Solicitud.objects.filter(usuario_asignado=self.request.user.id, tramite=tramite_id, estatus__nombre="ENVIADA").order_by("-fecha_inicio")
        context["solicitudes_concluidas"] = Solicitud.objects.filter(usuario_asignado=self.request.user.id, tramite=tramite_id, estatus__nombre__in=["AUTORIZADA"]).order_by("-fecha_inicio")

        context["tramite_asignado"] = False
        tramites_instance = NuevoTramite.objects.filter(asignar_a__in=[self.request.user.id])
        if tramites_instance:
            context["tramite_asignado"] = True

        context["tramites_pendientes_asignar"] = False
        solicitudes_sin_asignar_instance = Solicitud.objects.filter(usuario_asignado__isnull=True).exclude(estatus__nombre__in=["GUARDADA"])
        if solicitudes_sin_asignar_instance:
            context["tramites_pendientes_asignar"] = True

        return context

def TomarNuevaSolicitud(request):
    usuario_instance = User.objects.get(pk=request.user.id)
    solicitudes_instance = Solicitud.objects.filter(usuario_asignado__isnull=True).exclude(estatus__nombre__in=["GUARDADA"]).order_by("-id")[:1]
    if solicitudes_instance:
        for solicitud in solicitudes_instance:
            solicitud_instance = Solicitud.objects.get(pk=solicitud.id)
            solicitud_instance.usuario_asignado = usuario_instance
            solicitud_instance.save()
    else:
        return JsonResponse({'error': True, 'data': [], 'msj': "No se tienen solicitudes sin asignación" })


    return JsonResponse({'error': False, 'data': [], 'msj': "Registro asignado correctamente" })

def ValidarSolicitud(request):
    FormData = request.POST

    if FormData["solicitud_id"]:
        estatus_instance = Estatus_Solicitud.objects.get(nombre="ENVIADA")
        if FormData["estado"] == "0":
            estatus_instance = Estatus_Solicitud.objects.get(nombre="RECHAZADA")

        solicitud_instance = Solicitud.objects.get(pk=FormData["solicitud_id"])
        solicitud_instance.estatus = estatus_instance
        if FormData["estado"] == "0":
            solicitud_instance.observaciones = FormData["comentario"]

        solicitud_instance.save()

    # today = datetime.datetime.datetime.now()

    return JsonResponse({'error': False, 'data': FormData, 'msj': "Registro validado correctamente" })

def ListadoDetalleSolicitud(request):
    FormData = request.POST

    detalles_solicitud_instace = Detalle_Solicitud.objects.filter(solicitud_tramite=FormData["solicitud_id"]).values("es_obligatorio", "ruta_archivo", "requisito_nombre", "id", "requisito__id", "observaciones", "estatus", "usuario__username")

    return JsonResponse({'error': False, 'data': list(detalles_solicitud_instace) })


class SolicitudTramitesView(LoginRequiredMixin, TemplateView):
    template_name = 'tramites/tramite_en_linea/solicitud-tramites.html'

    def get_context_data(self, **kwargs):
        context = super(SolicitudTramitesView, self).get_context_data(**kwargs)
        tramite_id = self.kwargs.get('tramite_id')

        context['solicitud_id'] = ""
        context['solicitud_instance'] = ""
        solicitud_id = self.kwargs.get('pk')
        if solicitud_id and solicitud_id != "Nueva_solicitud":
            context['solicitud_id'] = solicitud_id
            context['solicitud_instance'] = Solicitud.objects.get(pk=solicitud_id)

        context['action'] = "modo_edicion"
        action = self.kwargs.get('action')
        if action == "ver":
            context['action'] = "modo_lectura"

        if action == "edicion":
            context['action'] = "modo_edicion_solicitud_revisada"

        context['tramite_id'] = tramite_id
        context["tramite"] = NuevoTramite.objects.get(pk=tramite_id)
        context["requisitos_tramite"] = Requisitos.objects.filter(tramite=tramite_id)


        context['perfil_usuario'] = "TRAMITES USUARIO"
        if User.objects.filter(username=self.request.user.username, groups__name__in=['TRAMITES ADMINISTRADOR']).exists():
            context['perfil_usuario'] = "TRAMITES ADMINISTRADOR"

        return context

def GuardarRequisitoSolicitudTramite(request):
    FormData = request.POST
    FileData = request.FILES

    requisitos_instance = Requisitos.objects.filter(tramite=int(FormData["tramite_id"]))
    user_instance = User.objects.get(pk=request.user.id)

    folio = FormData["folio"]
    nueva_solicitud = False

    if not FormData["folio"] and FormData["solicitud_id"] == "":
        nueva_solicitud = True
        folio_temporal = Detalle_solicitud_temporal.objects.order_by('-id')[:1]

        folio = 1
        if folio_temporal:
            for item in folio_temporal:
                folio = int(item.folio) + 1
    
    # Validamos que exista registro con el folio y id requisito seleccionado
    if FormData["solicitud_id"] and FormData["solicitud_id"] != "Nueva_solicitud":
        tb_detalle_solicitud_tmp_instance = Detalle_Solicitud.objects.filter(solicitud_tramite=FormData["solicitud_id"], requisito=FormData["requisito_id"])
    else:
        tb_detalle_solicitud_tmp_instance = Detalle_solicitud_temporal.objects.filter(folio=folio, requisito=FormData["requisito_id"])

    if tb_detalle_solicitud_tmp_instance:
        # Validamos que exista registro con el folio y id requisito seleccionado
        if FormData["solicitud_id"] and FormData["solicitud_id"] != "Nueva_solicitud":
            detalle_solicitud_tmp_instance = Detalle_Solicitud.objects.get(solicitud_tramite=FormData["solicitud_id"], requisito=FormData["requisito_id"])
        else:
            detalle_solicitud_tmp_instance = Detalle_solicitud_temporal.objects.get(folio=folio, requisito=FormData["requisito_id"])

        if detalle_solicitud_tmp_instance.ruta_archivo:
            a_ruta = str(detalle_solicitud_tmp_instance.ruta_archivo).split('/')
            path_ant = settings.MEDIA_ROOT + '/tramites/solicitudes_tramite/' + a_ruta[3]

            # Eliminamos el documento conforme a la ruta guardada
            remove(path_ant)

    path = ""
    nombre_archivo = ""
    # Guardar documento a la carpeta
    if "archivo_requisito_solicitud" in FileData:
        if FileData["archivo_requisito_solicitud"]:
            nombre_archivo = FileData["archivo_requisito_solicitud"].name
            a_nombre_archivo = str(nombre_archivo).split('.')
            archivo = FileData["archivo_requisito_solicitud"]

            folio_tramite = str(folio).rjust(6, '0')
            today = datetime.now()
            format_today =  today.strftime("%d%m%Y_%H%M%S")
            random_number = str(random.randint(0, 1000))

            rename_file = folio_tramite + format_today + random_number + '.' + a_nombre_archivo[1]

            path = settings.MEDIA_ROOT + '/tramites/solicitudes_tramite/' + rename_file

            with open(path, 'wb') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)

    if nueva_solicitud:
        # Guardar los registros de cada requisito según el trámite
        if requisitos_instance:
            for requisito in requisitos_instance:
                requisito_instance = Requisitos.objects.get(pk=requisito.id)

                if requisito.id == int(FormData["requisito_id"]):
                    Detalle_solicitud_temporal.objects.create(
                        folio = folio,
                        requisito = requisito_instance,
                        requisito_nombre = requisito.nombre,
                        es_obligatorio = requisito.obligatorio,
                        nombre_archivo = nombre_archivo,
                        ruta_archivo = path,
                        estatus = "Archivo capturado",
                        usuario = user_instance
                    ).save()
                else:
                    Detalle_solicitud_temporal.objects.create(
                        folio = folio,
                        requisito = requisito_instance,
                        requisito_nombre = requisito.nombre,
                        es_obligatorio = requisito.obligatorio,
                        estatus = "No capturado",
                        usuario = user_instance
                    ).save()
    else:
        if tb_detalle_solicitud_tmp_instance:
            if FormData["solicitud_id"] and FormData["solicitud_id"] != "Nueva_solicitud":
                detalle_solicitud_tmp_instance = Detalle_Solicitud.objects.get(solicitud_tramite=FormData["solicitud_id"], requisito=FormData["requisito_id"])
            else:
                detalle_solicitud_tmp_instance = Detalle_solicitud_temporal.objects.get(folio=folio, requisito=FormData["requisito_id"])

            detalle_solicitud_tmp_instance.nombre_archivo = nombre_archivo
            detalle_solicitud_tmp_instance.ruta_archivo = path

            if FormData["accion_vista"] == "modo_edicion_solicitud_revisada":
                detalle_solicitud_tmp_instance.estatus = "Archivo actualizado"
                detalle_solicitud_tmp_instance.observaciones = ""
            else:
                detalle_solicitud_tmp_instance.estatus = "Archivo capturado"
            
            if FormData["accion_vista"] == "modo_edicion_solicitud_revisada":
                solicitud_instance = Solicitud.objects.get(pk=FormData["solicitud_id"])
                estatus_solicitud_instance = Estatus_Solicitud.objects.get(pk=solicitud_instance.estatus.id)

                # Grabar quien envia solicitud
                usuario_instance = User.objects.get(pk=request.user.id)
                Historial_Solicitudes.objects.create(
                    usuario = usuario_instance,
                    solicitud_tramite = solicitud_instance,
                    estatus = estatus_solicitud_instance,
                    detalle_solicitud_tramite = detalle_solicitud_tmp_instance,
                    estatus_detalle_solicitud = "Archivo actualizado"
                ).save()
                
            detalle_solicitud_tmp_instance.save()
    
    return JsonResponse({'error': False, 'folio': folio, 'msj': "Archivo guardado correctamente" })

def EliminarDocsRequisitoSolicitud(request):
    FormData = request.POST

    # Validamos que exista registro con el folio y id requisito seleccionado
    if FormData["solicitud-id"] and FormData["solicitud-id"] != "Nueva_solicitud":
        detalle_solicitud_instance = Detalle_Solicitud.objects.get(pk=FormData["id_detalle_solicitud"])
    else:
        detalle_solicitud_instance = Detalle_solicitud_temporal.objects.get(folio=FormData["folio_temporal"], requisito=FormData["id_requisito"])

    if detalle_solicitud_instance.ruta_archivo:
        a_ruta = str(detalle_solicitud_instance.ruta_archivo).split('/')
        path_ant = settings.MEDIA_ROOT + '/tramites/solicitudes_tramite/' + a_ruta[3]

        # Eliminamos el documento conforme a la ruta guardada
        remove(path_ant)

    detalle_solicitud_instance.ruta_archivo = ""
    detalle_solicitud_instance.nombre_archivo = ""
    detalle_solicitud_instance.estatus = "No capturado"
    detalle_solicitud_instance.save()

    if FormData["accion_vista"] == "modo_edicion_solicitud_revisada":
        solicitud_instance = Solicitud.objects.get(pk=FormData["solicitud-id"])
        estatus_solicitud_instance = Estatus_Solicitud.objects.get(pk=solicitud_instance.estatus.id)

        # Grabar quien envia solicitud
        usuario_instance = User.objects.get(pk=request.user.id)
        Historial_Solicitudes.objects.create(
            usuario = usuario_instance,
            solicitud_tramite = solicitud_instance,
            estatus = estatus_solicitud_instance,
            detalle_solicitud_tramite = detalle_solicitud_instance,
            estatus_detalle_solicitud = "Archivo eliminado"
        ).save()

    return JsonResponse({'error': False, 'msj': "Archivo eliminado correctamente" })

def EnviarSolicitudTramite(request):
    FormData = request.POST

    detalle_solicitud_instance = Detalle_Solicitud.objects.filter(solicitud_tramite=FormData["solicitud_id"])

    if detalle_solicitud_instance:
        for detalle in detalle_solicitud_instance:
            if not detalle.nombre_archivo and detalle.es_obligatorio:
                return JsonResponse({'error': True, 'msj': "Tiene requisitos obligatorios sin documento capturado" })

    estatus_solicitud_instance = Estatus_Solicitud.objects.get(nombre="EN REVISION", is_active=True)
    if "solicitud_rechazada" in FormData:
        if FormData["solicitud_rechazada"] == 1:
            estatus_solicitud_instance = Estatus_Solicitud.objects.get(nombre="ENVIADA", is_active=True)

    solicitud_instance = Solicitud.objects.get(pk=FormData["solicitud_id"])
    solicitud_instance.estatus = estatus_solicitud_instance
    solicitud_instance.fecha_inicio = date.today()
    solicitud_instance.save()


    # Grabar quien envia solicitud
    usuario_instance = User.objects.get(pk=request.user.id)
    Historial_Solicitudes.objects.create(
        usuario = usuario_instance,
        solicitud_tramite = solicitud_instance,
        estatus = estatus_solicitud_instance,
    ).save()

    return JsonResponse({'error': False, 'msj': "Solicitud enviada correctamente" })

def AutorizarSolicitudes(request):
    FormData = request.POST

    detalles_solicitudes_instance = Detalle_Solicitud.objects.filter(solicitud_tramite=FormData["solicitud_id"])
    if detalles_solicitudes_instance:
        for detalle in detalles_solicitudes_instance:
            if detalle.estatus != "Archivo autorizado":
                return JsonResponse({'error': True, 'msj': "Debe de autorizar todos los requisitos de la solicitud" })

    usuario_instance = User.objects.get(pk=request.user.id)
    estatus_solicitud_instace = Estatus_Solicitud.objects.get(nombre="AUTORIZADA", is_active=True)

    solicitud_instance = Solicitud.objects.get(pk=FormData["solicitud_id"])
    solicitud_instance.fecha_fin = date.today()
    solicitud_instance.usuario_autorizo = usuario_instance
    solicitud_instance.estatus = estatus_solicitud_instace
    solicitud_instance.save()

    # Grabar quien autoriza solicitud
    Historial_Solicitudes.objects.create(
        usuario = usuario_instance,
        solicitud_tramite = solicitud_instance,
        estatus = estatus_solicitud_instace,
    ).save()

    return JsonResponse({'error': False, 'msj': "Solicitud guardada correctamente" })

def AceptarSolicitudesRequisitos(request):
    FormData = request.POST

    usuario_instance = User.objects.get(pk=request.user.id)

    if FormData["solicitud-id"]:
        estatus_solicitud_instance = Estatus_Solicitud.objects.get(nombre=FormData["solicitud-estatus"], is_active=True)
        solicitud_instance = Solicitud.objects.get(pk=FormData["solicitud-id"])
        solicitud_instance.estatus = estatus_solicitud_instance
        solicitud_instance.usuario_reviso = usuario_instance

        if FormData["solicitud-estatus"] == "RECHAZADA":
            solicitud_instance.observaciones = FormData["solicitud-observaciones"]
        else:
            solicitud_instance.observaciones = ""
        
        solicitud_instance.save()

        if FormData["solicitud-estatus"] == "ACEPTADA":
            detalles_solicitud_instance = Detalle_Solicitud.objects.filter(solicitud_tramite=FormData["solicitud-id"])
            if detalles_solicitud_instance:
                for detalle in detalles_solicitud_instance:
                    detalle_solicitud_instance = Detalle_Solicitud.objects.get(pk=detalle.id)
                    detalle_solicitud_instance.estatus = 'Archivo aceptado'
                    detalle_solicitud_instance.save()

        # Grabar quien envia solicitud
        Historial_Solicitudes.objects.create(
            usuario = usuario_instance,
            solicitud_tramite = solicitud_instance,
            observaciones = str(FormData["solicitud-observaciones"]).strip(),
            estatus = estatus_solicitud_instance,
        ).save()
    
    if FormData["requisito-detalle-id"]:
        detalle_solicitud_instance = Detalle_Solicitud.objects.get(pk=FormData["requisito-detalle-id"])
        detalle_solicitud_instance.estatus = FormData["solicitud-estatus"]

        if FormData["solicitud-estatus"] == "Archivo rechazado":
            detalle_solicitud_instance.observaciones = FormData["solicitud-observaciones"]

        detalle_solicitud_instance.save()

        solicitud_instance = Solicitud.objects.get(pk=detalle_solicitud_instance.solicitud_tramite.id)
        estatus_solicitud_instance = Estatus_Solicitud.objects.get(pk=solicitud_instance.estatus.id)

        # Grabar quien envia solicitud
        Historial_Solicitudes.objects.create(
            usuario = usuario_instance,
            solicitud_tramite = solicitud_instance,
            observaciones = str(FormData["solicitud-observaciones"]).strip(),
            estatus = estatus_solicitud_instance,
            detalle_solicitud_tramite = detalle_solicitud_instance,
            estatus_detalle_solicitud = FormData["solicitud-estatus"]
        ).save()

    return JsonResponse({'error': False, 'msj': "Solicitud guardada correctamente" })

def ListadoRequisitoSolicitudTramite(request):
    FormData = request.POST

    if FormData["solicitud_id"] and FormData["solicitud_id"] != "Nueva_solicitud":
        listado_requisitos = Detalle_Solicitud.objects.filter(
                solicitud_tramite=FormData["solicitud_id"]
            ).values("id", "requisito_nombre", "es_obligatorio", "ruta_archivo", "estatus", "nombre_archivo", "requisito__tiene_formato_default", "requisito__ruta_formato", "requisito__id", "observaciones")
    else:
        listado_requisitos = Detalle_solicitud_temporal.objects.filter(
                folio=FormData["folio_tmp"]
            ).values("id", "requisito_nombre", "es_obligatorio", "ruta_archivo", "estatus", "nombre_archivo", "requisito__tiene_formato_default", "requisito__ruta_formato", "requisito__id", "observaciones")

    return JsonResponse({'data': list(listado_requisitos) })

def GuardarSolicitudTramite(request):
    FormData = request.POST

    folio_temporal = FormData["folio"]
    detalle_solicitud_tmp_instance = Detalle_solicitud_temporal.objects.filter(folio=folio_temporal)
    tramite_instace = NuevoTramite.objects.get(pk=FormData["tramite_id"])
    estatus_solicitud_instace = Estatus_Solicitud.objects.get(nombre="GUARDADA", is_active=True)
    user_instance = User.objects.get(pk=request.user.id)

    if detalle_solicitud_tmp_instance:
        for detalle in detalle_solicitud_tmp_instance:
            if not detalle.nombre_archivo and detalle.es_obligatorio:
                return JsonResponse({'error': True, 'msj': "Tiene requisitos que son obligatorios y no tiene algún documento capturado" })
    
    solicitudes = Solicitud.objects.order_by('-id')[:1]

    folio_solicitud = 1
    if solicitudes:
        for item in solicitudes:
            folio_solicitud = int(item.folio) + 1
    
    if FormData["solicitud-id"]:
        solicitud_instance = Solicitud.objects.get(pk=FormData["solicitud-id"])
        # solicitud_instance.fecha_inicio = FormData["solicitud-fecha_inicio"]
        # solicitud_instance.fecha_fin = FormData["solicitud-fecha_fin"]
        # solicitud_instance.fecha_vigencia = FormData["solicitud-fecha_vigencia"]
        solicitud_instance.save()
    else:
        solicitud_id = Solicitud.objects.create(
            folio = folio_solicitud,
            tramite = tramite_instace,
            usuario = user_instance,
            estatus = estatus_solicitud_instace,
        ).pk

        solicitud_instance = Solicitud.objects.get(pk=solicitud_id)

        if detalle_solicitud_tmp_instance:
            for detalle in detalle_solicitud_tmp_instance:

                requisito_instance = Requisitos.objects.get(pk=detalle.requisito.id)

                Detalle_Solicitud.objects.create(
                    requisito = requisito_instance,
                    requisito_nombre = detalle.requisito.nombre,
                    es_obligatorio = detalle.es_obligatorio,
                    nombre_archivo = detalle.nombre_archivo,
                    ruta_archivo = detalle.ruta_archivo,
                    estatus = detalle.estatus,
                    usuario = user_instance,
                    solicitud_tramite = solicitud_instance,
                    folio_temporal = folio_temporal,
                ).save()
    
    # Grabar quien envia solicitud
    usuario_instance = User.objects.get(pk=request.user.id)
    Historial_Solicitudes.objects.create(
        usuario = usuario_instance,
        solicitud_tramite = solicitud_instance,
        estatus = estatus_solicitud_instace,
    ).save()

    return JsonResponse({'error': False, 'msj': "Solicitud guardada correctamente" })      


class VistaUsuario(LoginRequiredMixin,ListView):
    template_name = 'tramites/vista-usuarios.html'      
    context_object_name = 'vista'

    def get_queryset(self):
        usuarios = NuevoTramite.objects.filter(estatus=2)      

        return usuarios


class RechazarView(UpdateView): 
    queryset = NuevoTramite.objects.all()
    template_name = 'tramites/modal-rechazar.html'
    form_class = FormNuevoTramite 

    def get_context_data(self, **kwargs):
        context = super(RechazarView, self).get_context_data(**kwargs)     
        idvista = self.kwargs.get('pk') 

        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='TRAMITES ADMINISTRADOR'):
            context['permission'] = 'TRAMITES ADMINISTRADOR'
        elif User.objects.filter(username=user, groups__name__contains='TRAMITES EDITOR'): 
            context['permission'] = 'TRAMITES EDITOR'

        context['verEditar'] = NuevoTramite.objects.filter(id=idvista)
        context['activar_vista'] = NuevoTramite.objects.all() 
        # context['comentarios'] = Comentarios.objects.filter(id=idvista)  

        return context 
    
    def get_success_url(self):
        messages.success(self.request, 'se guardo con exito')      
        return reverse_lazy('tramites_app:tramites-servicios')  

def RechazarEdicion(request):  

    FormData = request.POST

    activar_instance = NuevoTramite.objects.get(pk=FormData['activar'])
    activar_instance.comentarios = FormData['comentarios']
    catalogo_estatus_instance = Estatus.objects.get(esta_tus=FormData['estatus']) 
    activar_instance.estatus = catalogo_estatus_instance 
    activar_instance.save()

    return JsonResponse({'error': False, 'msj': "Documento en proceso" })

class PublicarView(ListView):
    template_name = 'tramites/modal-publicar.html' 
    context_object_name = 'publicar' 

    def get_queryset(self):
        publicar = NuevoTramite.objects.all()  

        return publicar  

    def get_context_data(self, **kwargs):
        context = super(PublicarView, self).get_context_data(**kwargs)     
        idvista = self.kwargs.get('pk') 

        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='TRAMITES ADMINISTRADOR'):
            context['permission'] = 'TRAMITES ADMINISTRADOR'
        elif User.objects.filter(username=user, groups__name__contains='TRAMITES EDITOR'): 
            context['permission'] = 'TRAMITES EDITOR'    

        context['verEditar'] = NuevoTramite.objects.filter(id=idvista)
        context['activar_vista'] = NuevoTramite.objects.all()

        return context 

def PublicarVista(request):   

    FormData = request.POST

    activar_instance = NuevoTramite.objects.get(pk=FormData['activar'])
    catalogo_estatus_instance = Estatus.objects.get(esta_tus=FormData['estatus'])   
    activar_instance.estatus = catalogo_estatus_instance
    activar_instance.save()

    return JsonResponse({'error': False, 'msj': "Documento en proceso" })

class ObservacionesView(ListView):
    template_name = 'tramites/modal-rechazar.html'
    context_object_name = 'observaciones'  

    def get_queryset(self):
        comentario = Observaciones.objects.all()

        return comentario
    
    def get_context_data(self, **kwargs):   
        context = super(ObservacionesView, self).get_context_data(**kwargs)     
        idvista = self.kwargs.get('pk') 

        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='TRAMITES ADMINISTRADOR'):
            context['permission'] = 'TRAMITES ADMINISTRADOR'
        elif User.objects.filter(username=user, groups__name__contains='TRAMITES EDITOR'): 
            context['permission'] = 'TRAMITES EDITOR'

        context['verObservaciones'] = NuevoTramite.objects.filter(id=idvista)

        return context 


def ComentariosDetalle(request):     

    FormData = request.POST  
    
    nuevo_tramite = NuevoTramite.objects.get(pk=FormData['detalle'])
    estatus_instance = Estatus.objects.get(esta_tus=FormData['estatus'])
    nuevo_tramite.estatus = estatus_instance       

    nuevo_tramite.comentarios = FormData['comentario']
     
    nuevo_tramite.save()  

    Observaciones.objects.create(
        detalle = FormData['comentario'], 
        usuario = User.objects.get(pk=request.user.id),
        tramite = nuevo_tramite
    ).save()    

    return JsonResponse({'error':False, 'msj': "Datos guardados correctamente"})


class NuevaPrestacion(LoginRequiredMixin , SuccessMessageMixin ,CreateView):    
    Model = NuevoTramite         
    template_name = 'tramites/modal-nueva-prestacion.html'
    form_class = FormNuevoTramite   

    def get_success_url(self):
        messages.success(self.request, 'se guardo con exito')
        return reverse_lazy('tramites_app:tramites-servicios') 

class ModalDatos(UpdateView):    
    queryset = NuevoTramite.objects.all()
    template_name = 'tramites/modal-editar-datos.html'    
    form_class = FormNuevoTramite 

    def get_context_data(self, **kwargs):  
        context = super(ModalDatos, self).get_context_data(**kwargs)      
        idvista = self.kwargs.get('pk') 

        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='TRAMITES ADMINISTRADOR'):
            context['permission'] = 'TRAMITES ADMINISTRADOR'
        elif User.objects.filter(username=user, groups__name__contains='TRAMITES EDITOR'):
            context['permission'] = 'TRAMITES EDITOR'
        
        context['verEditar'] = NuevoTramite.objects.filter(id=idvista)        
        
        context['activar_vista'] = NuevoTramite.objects.all() 

        context['tablaVista'] = Observaciones.objects.filter(is_active=True,tramite=idvista).order_by('detalle') 
        context['pk']  = idvista 

        return context  

    def get_success_url(self):
        messages.success(self.request, 'se guardo con exito')
        return reverse_lazy('tramites_app:tramites-servicios') 

class AsignarMdal(UpdateView):    
    model = NuevoTramite 
    template_name = 'tramites/asignados.html'        
    # form_class = FormNuevoTramite  
    fields = ['asignar_a']        

    def get_context_data(self, **kwargs):
        context = super(AsignarMdal, self).get_context_data(**kwargs)      
        idvista = self.kwargs.get('pk')   

        user = self.request.user.username   
        if User.objects.filter(username=user, groups__name__contains='TRAMITES ADMINISTRADOR'):
            context['permission'] = 'TRAMITES ADMINISTRADOR'
        elif User.objects.filter(username=user, groups__name__contains='TRAMITES EDITOR'):
            context['permission'] = 'TRAMITES EDITOR'

        context['verEditar'] = NuevoTramite.objects.filter(id=idvista)         
        
        context['activar_vista'] = NuevoTramite.objects.all() 

        context['tablaVista'] = Observaciones.objects.filter(is_active=True,tramite=idvista).order_by('detalle') 
        context['pk']  = idvista    

        return context     


    def get_success_url(self):      
        messages.success(self.request, 'se guardo con exito')              
        return reverse_lazy('tramites_app:tramites-servicios')     
