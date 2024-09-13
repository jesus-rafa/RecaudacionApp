import json
import random
import pytz
from datetime import date, datetime

from django.http.response import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic import (
    ListView,
    CreateView, 
    UpdateView
)
from django.views.generic.edit import DeleteView, FormView
from django.db.models import Q, Sum, F, Count
from django.db.models.functions import ExtractDay
from django.db import connection
from django.db.models import Case, Count, F, Q, Sum, When, query

from applications.rec.models import Contacto, REC
from applications.users.models import User
from applications.home.models import Codigos_Maestros
from applications.padrones.managers import ProgramaManager
from applications.home.models import Codigos_Maestros
from applications.users.mixins import GlobalMixin, CRUDMixin

from .models import Programa_Padrones, Detalle_Padrones, Pagos_Padrones, Archivos_Padrones, Envio_Insumos_Programas_Padrones
from .forms import ArchivosForm, ProgramacionForm, DetalleForm, PagosForm, TurnarForm

# ============================= ListView ================================================ #


class Turnar_Programacion(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "padrones/turnar.html"
    success_url = reverse_lazy('padrones_app:lista-programacion-2')
    form_class = TurnarForm
    success_message = "RFCs asigandos correctamente!"

    def form_valid(self, form):
        seguimiento = form.cleaned_data['seguimiento']
        start = str(seguimiento).find('(') + 1
        end = str(seguimiento).find(')')   
        
        new_control = str(date.today().month) + '-' + str(date.today().year)

        if form.cleaned_data['lista']:
            list_id = form.cleaned_data['lista'].split(',')
            Programa_Padrones.objects.filter(id__in=list_id).update(seguimiento=str(seguimiento)[start:end], no_control=new_control, area='PADRONES')

        return super(Turnar_Programacion, self).form_valid(form)


class Reporte_Padrones(GlobalMixin, ListView):
    template_name = 'padrones/reporte_padrones.html'
    model = Programa_Padrones
    context_object_name = 'programacion'
    
    def get_queryset(self):
        return Programa_Padrones.objects.contribuyentes_por_mes()
        
        
class Reporte_Detalle(LoginRequiredMixin, ListView):
    template_name = 'padrones/reporte_detalle.html'
    context_object_name = 'detalle'

    def get_queryset(self):
      
        no_control = self.kwargs.get('folio')

        if Programa_Padrones.objects.filter(no_control=no_control).exists():
            queryset = Programa_Padrones.objects.detalle_mes(
                no_control=no_control,
            )
        else:
            queryset = None

        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(Reporte_Detalle, self).get_context_data(**kwargs)

        context['folio'] = self.kwargs.get('folio')

        return context
            

class Lista_Programacion(GlobalMixin, ListView):
    template_name = 'padrones/lista_programacion.html'
    model = Programa_Padrones
    context_object_name = 'programacion'

    def get_context_data(self, **kwargs):
        context = super(Lista_Programacion, self).get_context_data(**kwargs)

        context['filter_seguimiento'] = User.objects.filter(groups__name__contains='PADRONES')
        context['filter_etapa'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE_PADRONES').order_by('id') 
        context['filter_estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS_PADRONES').order_by('id')        
        #context['filter_programa'] = Codigos_Maestros.objects.filter(codigo='XXPROGRAM_PADRONES')   
        context['filter_programa'] = Programa_Padrones.objects.order_by('programa').values('programa').distinct()
        context['filter_area'] = Programa_Padrones.objects.order_by('area').values('area').distinct()

        return context
    
    def get_queryset(self):

        username = self.request.user.username
        user = self.request.user.nombres + ' ' + self.request.user.apellidos
        cursor = connection.cursor()

        kword=self.request.GET.get("kword")
        userEfe=self.request.GET.get("user")
        etapa=self.request.GET.get("etapa")
        status=self.request.GET.get("estatus")
        program=self.request.GET.get("program")
        area=self.request.GET.get("area")
        top=self.request.GET.get("top",10)
        
        if User.objects.filter(username=username, groups__name__in=['JEFE PADRONES']).exists():
            area = "PADRONES" if area == "" else area
            sql = f'''
                    SELECT 
                        *
                    FROM 
                        padrones_seguimiento 
                    WHERE 
                        (
                            rfc ILIKE '%{kword}%' 
                            OR nombre ILIKE '%{kword}%'
                        )
                        AND seguimiento ILIKE '%{userEfe}%' 
                        AND etapa ILIKE '%{etapa}%' 
                        AND estatus ILIKE '%{status}%' 
                        AND programa ILIKE '%{program}%' 
                        AND area ILIKE '%{area}%'
                    ORDER BY 
                        dias_sin_acciones DESC
                    LIMIT {top}
                   ;'''
        else:
            sql = f'''
                    SELECT 
                        *
                    FROM 
                        padrones_seguimiento 
                    WHERE 
                        (
                            rfc ILIKE '%{kword}%' 
                            OR nombre ILIKE '%{kword}%'
                        )
                        AND seguimiento = '{user.upper()}'
                        AND etapa ILIKE '%{etapa}%' 
                        AND estatus ILIKE '%{status}%' 
                        AND programa ILIKE '%{program}%' 
                        AND area ILIKE '%{area}%'
                    ORDER BY 
                        dias_sin_acciones DESC
                    LIMIT {top}
                   ;'''
        #sql = f'''SELECT * FROM padrones_seguimiento WHERE seguimiento = '{user.upper()}' ORDER BY dias_sin_acciones DESC;'''
        
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        queryset = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            queryset.append(dict(rowset))        
        return queryset



class Programas_Especiales(GlobalMixin, TemplateView):
    template_name = 'padrones/programas_especiales.html'

    def get_context_data(self, **kwargs):
        context = super(Programas_Especiales,
                        self).get_context_data(**kwargs)

        username = self.request.user.username

        context['grandes_contribuyentes'] = Programa_Padrones.objects.programas_especiales(
            username=username,
            programa='GRANDES CONTRIBUYENTES'
        )

        context['municipios'] = Programa_Padrones.objects.programas_especiales(
            username=username,
            programa='MUNICIPIOS'
        )

        context['publicas'] = Programa_Padrones.objects.programas_especiales(
            username=username,
            programa='INSTITUCIONES PUBLICAS'
        )
        
        context['contratistas'] = Programa_Padrones.objects.programas_especiales(
            username=username,
            programa='CONTRATISTAS'
        )

        return context
        
        
class Lista_Programacion_Padrones(GlobalMixin, ListView):
    template_name = 'padrones/lista_programacion_padrones.html'
    
    model = Programa_Padrones
    context_object_name = 'programacion'

    def get_queryset(self):
        user = self.request.user.username
        exclude_programs = ['GRANDES CONTRIBUYENTES', 'CONTRATISTAS', 'MUNICIPIOS', 'INSTITUCIONES PUBLICAS']
        
        if User.objects.filter(username=user, groups__name__in=['DIRECTOR']).exists():
            # queryset = Programa_Padrones.objects.filter(
                # ~Q(seguimiento=''),
                # ~Q(etapa='CONCLUIDO'),
                # ~Q(estatus='CONCLUIDO')
            # )
            queryset = Programa_Padrones.objects.exclude(
                Q(seguimiento='') | Q(etapa='CONCLUIDO') | Q(estatus='CONCLUIDO')
            )
            #queryset = Programa_Padrones.objects.all()[:10]
            
            #queryset = None
        else:
            queryset = Programa_Padrones.objects.filtrar_seguimiento(
                username = self.request.user.username,
                excluir_programas = exclude_programs
            )
            
        #queryset = None
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Lista_Programacion_Padrones,
                        self).get_context_data(**kwargs)

        username = self.request.user.username

        context['grandes_contribuyentes'] = Programa_Padrones.objects.programas_especiales(
            username=username,
            programa='GRANDES CONTRIBUYENTES'
        )

        context['municipios'] = Programa_Padrones.objects.programas_especiales(
            username=username,
            programa='MUNICIPIOS'
        )

        context['publicas'] = Programa_Padrones.objects.programas_especiales(
            username=username,
            programa='INSTITUCIONES PUBLICAS'
        )
        
        context['contratistas'] = Programa_Padrones.objects.programas_especiales(
            username=username,
            programa='CONTRATISTAS'
        )

        return context


class Admin_Programacion(LoginRequiredMixin, ListView):
    template_name = 'padrones/admin_programacion.html'
    context_object_name = 'programacion'

    def get_queryset(self):
        programa_id = self.kwargs.get('id')
        return Programa_Padrones.objects.filter(id=programa_id)

    def get_context_data(self, **kwargs):
        context = super(Admin_Programacion, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')

        obj_Programa = Programa_Padrones.objects.filter(id=id)

        if REC.objects.filter(rfc=obj_Programa[0].rfc).exists():
            obj_REC = REC.objects.filter(rfc=obj_Programa[0].rfc)
            id_contacto = obj_REC[0].id
        else:
            id_contacto = 0

        if Detalle_Padrones.objects.filter(programa_id = id, estatus__contains='NOTIFICADO').exists():

            if Detalle_Padrones.objects.filter(programa_id = id, estatus__contains='CONCLUIDO').exists():
                obj_notificado = Detalle_Padrones.objects.filter(
                    programa_id = id,
                    estatus__contains = 'NOTIFICADO'
                )
                obj_concluido = Detalle_Padrones.objects.filter(
                    programa_id = id,
                    estatus__contains = 'CONCLUIDO'
                )
                dias = (obj_concluido[0].fecha - obj_notificado[0].fecha).days
            else:
                today = date.today()

                obj = Detalle_Padrones.objects.filter(
                    programa_id = id,
                    estatus__contains = 'NOTIFICADO'
                )
                dias = (today - obj[0].fecha).days
        else:
            dias = 0

        context['dias'] = dias
        context['detalles'] = Detalle_Padrones.objects.filter(programa_id = id, is_active=True).order_by('fecha')     
        context['archivos'] = Archivos_Padrones.objects.filter(programa_id = id, is_active=True)    
        context['pagos_presuntiva'] = Pagos_Padrones.objects.filter(programa_id = id, presuntiva=True)       
        #context['pagos'] = Pagos_Padrones.objects.filter(programa_id = id, presuntiva=False)      
        context['contactos'] =  Contacto.objects.detalle_all(id_contacto)
        
        cursor = connection.cursor()
        mySql = f"""select fecha,
                    tipo,
                    periodo,
                    ejercicio,
                    comentarios,
                    sum(impuesto) impuesto, 
                    sum(accesorios) accesorios, 
                    sum(recargos) recargos 
                from padrones_pagos_padrones
                    where programa_id_id = {id}
                    group by fecha, tipo, periodo, ejercicio, comentarios	"""
    
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))

        context['pagos'] = result

        return context
    

# ============================= DeleteView ================================================ #



class Eliminar_Archivo(CRUDMixin, DeleteView):
    permission_required = ('delete_archivos_padrones')
    
    model = Archivos_Padrones
    template_name = 'rec/eliminar_datos.html'

    def delete(self, request, *args, **kwargs):
        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            obj_archivo = self.get_object()
            obj_archivo.is_active=False
            obj_archivo.save()

            message = 'Archivo Eliminado!'
            error = 'No hay error!'
            response = JsonResponse({'message': message, 'error': error})
            return response
        else:
            return reverse_lazy('rec_app:lista-rec')

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

class Eliminar_Detalle(CRUDMixin, DeleteView):
    permission_required = ('delete_detalle_padrones')
    
    model = Detalle_Padrones
    template_name = 'rec/eliminar_datos.html'

    def delete(self, request, *args, **kwargs):
        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            obj_detalle = self.get_object()
            obj_detalle.is_active=False
            obj_detalle.save()

            message = 'Detalle Eliminado!'
            error = 'No hay error!'
            response = JsonResponse({'message': message, 'error': error})
            return response
        else:
            return reverse_lazy('rec_app:lista-rec')

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']
                
                
class Eliminar_Pagos(CRUDMixin, DeleteView):
    permission_required = ('delete_pagos_padrones')

    model = Pagos_Padrones
    template_name = 'rec/eliminar_datos.html'

    def delete(self, request, *args, **kwargs):
        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            obj_pagos = self.get_object()
            obj_pagos.is_active=False
            obj_pagos.save()

            message = 'Pago Eliminado!'
            error = 'No hay error!'
            response = JsonResponse({'message': message, 'error': error})
            return response
        else:
            return reverse_lazy('rec_app:lista-rec')

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']



# ============================= UpdateView ================================================ #

class Editar_Archivo(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_archivos_padrones')
    
    model = Archivos_Padrones
    template_name = 'padrones/editar/editar_archivos.html'
    form_class = ArchivosForm
    success_message = 'Archivo actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Editar_Archivo, self).get_context_data(**kwargs)

        obj = self.get_object()
        selected_tipo = Codigos_Maestros.objects.filter(comentario=obj.tipo)
        context['selected_tipo'] = selected_tipo[0].id
        
        return context

    def get_form_kwargs(self):
        kwargs = super(Editar_Archivo, self).get_form_kwargs()

        obj = Archivos_Padrones.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id_id)

        return kwargs 

    def get_success_url(self):
        return reverse_lazy('padrones_app:admin-programacion-2', kwargs={'id': self.object.programa_id_id })


class Editar_Detalle(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_detalle_padrones')
    
    model = Detalle_Padrones
    template_name = 'padrones/editar/editar_detalle.html'
    form_class = DetalleForm
    success_message = 'Seguimiento actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Editar_Detalle, self).get_context_data(**kwargs)

        obj = self.get_object()
        selected_etapa = Codigos_Maestros.objects.filter(codigo='XXSTAGE_PADRONES', comentario=obj.etapa)
        context['selected_etapa'] = selected_etapa[0].id
        selected_estatus = Codigos_Maestros.objects.filter(codigo='XXSTATUS_PADRONES', comentario=obj.estatus)
        context['selected_estatus'] = selected_estatus[0].id
        
        context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE_PADRONES').order_by('id')
        context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS_PADRONES').order_by('id')
        
        return context

    def get_form_kwargs(self):
        kwargs = super(Editar_Detalle, self).get_form_kwargs()

        obj = Detalle_Padrones.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id)

        return kwargs
        
    def form_valid(self, form): 
        etapa = form.cleaned_data['etapa']
        obj = Codigos_Maestros.objects.filter(id=etapa)    
        estatus = form.cleaned_data['estatus']
        obj2 = Codigos_Maestros.objects.filter(id=estatus)

        form.instance.usuario = self.request.user.username
        form.instance.etapa = str(obj[0].comentario)
        form.instance.estatus = str(obj2[0].comentario)

        return super(Editar_Detalle, self).form_valid(form)


    def get_success_url(self):
        return reverse_lazy('padrones_app:admin-programacion-2', kwargs={'id': self.object.programa_id })



class Editar_Pago(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_pagos_padrones')
    
    model = Pagos_Padrones
    template_name = 'padrones/editar/editar_pagos.html'
    form_class = PagosForm
    success_message = 'Pago actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Editar_Pago, self).get_context_data(**kwargs)

        obj = self.get_object()
        selected_tipo = Codigos_Maestros.objects.filter(comentario=obj.tipo)
        context['selected_tipo'] = selected_tipo[0].id
        
        return context

    def get_form_kwargs(self):
        kwargs = super(Editar_Pago, self).get_form_kwargs()

        obj = Pagos_Padrones.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id)

        return kwargs

    def get_success_url(self):
        return reverse_lazy('padrones_app:admin-programacion-2', kwargs={'id': self.object.programa_id })

# ============================= CreateView ================================================ #

class Alta_Pagos(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_pagos_padrones')
    
    model = Pagos_Padrones
    template_name = 'padrones/crear/alta_pagos.html'
    form_class = PagosForm
    success_message = 'Pago creado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Alta_Pagos, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']
        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Pagos, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user.username

        return super(Alta_Pagos, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('padrones_app:admin-programacion-2', kwargs={'id': self.object.programa_id })


class Alta_Archivos(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_archivos_padrones')
     
    model = Archivos_Padrones
    template_name = 'padrones/crear/alta_archivos.html'
    form_class = ArchivosForm
    success_message = 'Archivo cargado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Alta_Archivos, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']
        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Archivos, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user.username

        return super(Alta_Archivos, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('padrones_app:admin-programacion-2', kwargs={'id': self.object.programa_id })


class Alta_Programacion(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Programa_Padrones
    template_name = 'padrones/crear/alta_programacion.html'
    form_class = ProgramacionForm
    success_url = reverse_lazy('padrones_app:lista-programacion-2')
    success_message = 'Folio creado exitosamente!'

    def form_valid(self, form):
        form.instance.usuario = self.request.user.username
        form.instance.estatus = 'VALIDACION'
        
        seguimiento = form.cleaned_data['seguimiento']
        start = str(seguimiento).find('(') + 1
        end = str(seguimiento).find(')')

        form.instance.seguimiento = str(seguimiento)[start:end]

        

        return super(Alta_Programacion, self).form_valid(form)
  
class Alta_Detalle(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Detalle_Padrones
    template_name = 'padrones/crear/alta_detalle.html'
    form_class = DetalleForm
    success_message = 'Detalle creado exitosamente!'
    
    def get_context_data(self, **kwargs):
        context = super(Alta_Detalle, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']
        
        context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE_PADRONES').order_by('id')
        context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS_PADRONES').order_by('id')
        
        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Detalle, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):
        id = form.cleaned_data.get('programa_id')
        
        etapa = form.cleaned_data['etapa']
        obj = Codigos_Maestros.objects.filter(id=etapa)
        estatus = form.cleaned_data['estatus']
        obj2 = Codigos_Maestros.objects.filter(id=estatus)
        
        instance = Programa_Padrones.objects.get(id = str(id))
        instance.etapa = str(obj[0].comentario)
        instance.estatus = str(obj2[0].comentario)
        instance.save()

        form.instance.usuario = self.request.user.username
        form.instance.etapa = str(obj[0].comentario)
        form.instance.estatus = str(obj2[0].comentario)

        return super(Alta_Detalle, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('padrones_app:admin-programacion-2', kwargs={'id': self.object.programa_id })


# ============================= Views ================================================ #

class Ver_Programacion(LoginRequiredMixin, DetailView):
    model = Programa_Padrones
    template_name = 'padrones/consulta/ver_programacion.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Programacion, self).get_context_data(**kwargs)
        context['detalles'] = Detalle_Padrones.objects.filter(programa_id=self.kwargs.get('pk'), is_active=True)    
        context['pagos'] = Pagos_Padrones.objects.filter(programa_id = self.kwargs.get('pk'), presuntiva=False) 

        return context 

class Ver_Archivos(LoginRequiredMixin, DetailView):
    model = Programa_Padrones
    template_name = 'padrones/consulta/ver_archivos.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Archivos, self).get_context_data(**kwargs)
        context['archivos'] = Archivos_Padrones.objects.filter(programa_id=self.kwargs.get('pk'))    
        
        return context

class Ver_Pagos(LoginRequiredMixin, DetailView):
    model = Programa_Padrones
    template_name = 'padrones/consulta/ver_pagos.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Pagos, self).get_context_data(**kwargs)
        id = self.kwargs.get('pk')

        context['pagos_presuntiva'] = Pagos_Padrones.objects.filter(programa_id = id, presuntiva=True)      
        context['pagos'] = Pagos_Padrones.objects.filter(programa_id = id, presuntiva=False)       
                
        return context


class EnvioInsumoView(ListView):
    template_name = "padrones/envio_insumo.html"
    context_object_name = 'programas_padrones'

    def get_queryset(self):
        query_set = Programa_Padrones.objects.filter(programa="REFRENDO 5").order_by("id")
        return query_set

    def get_context_data(self, **kwargs):
        context = super(EnvioInsumoView, self).get_context_data(**kwargs)
        return context

def GuardarMasivoProgramasPadrones(request):
    FormData = request.POST
    FileData = request.FILES

    if not FileData["archivo_programa_padrones"]:
        return JsonResponse({'msj': "No se adjunto nungún archivo", 'data': [], 'error': True})

    nombre_archivo = FileData["archivo_programa_padrones"].name
    a_nombre_archivo = str(nombre_archivo).split('.')
    archivo = FileData["archivo_programa_padrones"]

    today = datetime.now()
    format_today =  today.strftime("%d%m%Y_%H%M%S")
    random_number = str(random.randint(0, 1000))

    rename_file = format_today + random_number + '.' + a_nombre_archivo[1]

    archivo.name = rename_file

    path = settings.MEDIA_ROOT + '/insumos/archivos_masivos/' + rename_file

    with open(path, 'wb') as destination:
        for chunk in archivo.chunks():
            destination.write(chunk)

    row_count = 0
    with open(path,"rU") as f:
        row_count = sum(1 for row in f)
    
    if row_count >= 802:
        return JsonResponse({'msj': "No se pueden cargar más de 800 registros por archivo", 'data': [], 'error': True})
    
    user = request.user.username
    
    envio_insumo_id = Envio_Insumos_Programas_Padrones.objects.create(
        usuario = User.objects.get(pk=request.user.id),
        nombre_archivo = rename_file,
        ruta_archivo = path,
    ).pk

    # Ejecutar Funcion
    cursor = connection.cursor()
    sql = f''' SELECT cargar_programas_padrones('{archivo}','{user}','{envio_insumo_id}'); '''
    cursor.execute(sql)
    resultado = cursor.fetchone()

    datos_respuesta = ""
    if resultado[0].split(':')[1] == 'ERROR':
        datos_respuesta = resultado[0].split(':')[0]
        message ='Se generaron algunos errores, favor de revisar los datos que no se cargaron.'
    else:
        message = 'Todos los datos se cargaron correctamente.'
    
    # Validar si tiene algun registro relacionado
    programa_padrones_instance = Programa_Padrones.objects.filter(registro_masivo=True, envio_insumos_programa_padrones=envio_insumo_id)
    if not programa_padrones_instance:
        # Si no existe eliminar el registro de la carga de archivo
        envio_insumos_programa_padrones_instance = Envio_Insumos_Programas_Padrones.objects.get(pk=envio_insumo_id)
        envio_insumos_programa_padrones_instance.delete()
    
    return JsonResponse({'msj': message, 'data': datos_respuesta, 'error': False})
