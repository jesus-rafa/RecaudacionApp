from datetime import date
import xmltodict
import requests
import json
import ast
from django.core.serializers import serialize
from django.http.response import JsonResponse
from django.db import connection
from django.contrib import messages
from django.shortcuts import redirect, render
from django.shortcuts import render, HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic import (
    ListView,
    CreateView, 
    UpdateView,
    View
)
from django.views.generic.edit import DeleteView, FormView
from django.db.models import Sum, Q, Count, OuterRef, Subquery
from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db import transaction
from applications.rec.models import Contacto, REC
from applications.rec.functions import generar_excel_orm
from applications.home.models import Codigos_Maestros
from applications.users.models import User
from applications.transferidos.models import Programa_Transferidos
from applications.promocion.models import Opciones
from applications.rec.models import REC_Notificados, REC

from .models import Impuestos, Programa, Detalle, Pagos, Archivos, Contribuyentes, Archivos_Contribuyente
from .forms import (
    ArchivosForm, 
    ArchivosForm2, 
    ProgramacionForm, 
    DetalleForm, 
    PagosForm, 
    ContribuyenteForm, 
    AsignarForm, 
    ReasignarForm, 
    CierreForm, 
    SolicitarForm, 
    ArchivosSolicitudForm, 
    CerrarApoyoForm,
    EstatusCierre,
    CerrarRFCForm,
    ContribuyentesForm,
    CerrarAnalisisForm,
    ImpuestosForm,
    Archivos_Contribuyente_Form
)
from applications.users.mixins import GlobalMixin, CRUDMixin

# ============================= ListView ================================================ #


class Lista_Programacion(GlobalMixin, ListView):
    template_name = 'programacion/lista_programacion.html'
    model = Programa
    context_object_name = 'programacion'
    
    def get_queryset(self):
        user = self.request.user.nombres + ' ' + self.request.user.apellidos
        username = self.request.user.username
        cursor = connection.cursor()

        if User.objects.filter(username=username, groups__name__in=['DIRECTOR','COORDINACION VIGILANCIA','JEFE COBRO 2']).exists():
            #queryset = Programa.objects.filtrar_todos()
            sql = f'''SELECT * FROM dias_seguimiento;'''

        else:
            #queryset = Programa.objects.filtrar_seguimiento(username = user)
            sql = f'''SELECT * FROM dias_seguimiento WHERE seguimiento = '{user.upper()}';'''
        
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        queryset = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            queryset.append(dict(rowset))
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(Lista_Programacion, self).get_context_data(**kwargs)

        user = self.request.user.username

        context['plan_pagos'] = Programa.objects.filter(
            detalle_programa__estatus='PLAN DE PAGOS'
            #seguimiento__icontains=user
        ).exclude(
            estatus='CONCLUIDO'
        ).distinct('id')

        context['apoyo_ejecucion'] = Programa.objects.filter(
            detalle_programa__estatus='SOLICITUD ACEPTADA'
            #seguimiento__icontains=user
        ).exclude(
            estatus='CONCLUIDO'
        ).distinct('id')

        total = Pagos.objects.filter(
            programa_id__seguimiento=user,
            fecha__range=['2023-01-01','2023-12-31'],
            is_active=True
        ).aggregate(
            total_recargos=Sum('recargos'), 
            total_accesorios=Sum('accesorios'), 
            total_impuesto=Sum('impuesto')
        )

        if total['total_recargos'] != None:
            recargos = total['total_recargos']
        else:
            recargos = 0

        if total['total_accesorios'] != None:
            accesorios = total['total_accesorios']
        else: 
            accesorios = 0

        if total['total_impuesto'] != None:
            impuesto = total['total_impuesto']
        else:
            impuesto = 0

        context['acumulado'] = recargos + accesorios + impuesto

        return context


class Seguimiento_Vigilancia(LoginRequiredMixin, TemplateView):
    template_name = 'programacion/seguimiento.html'
        
    def get_context_data(self, **kwargs):
        context = super(Seguimiento_Vigilancia, self).get_context_data(**kwargs)

        user = self.request.user.nombres + ' ' + self.request.user.apellidos
        username = self.request.user.username
        cursor = connection.cursor()

        if User.objects.filter(username=username, groups__name__in=['DIRECTOR','COORDINACION VIGILANCIA','JEFE COBRO 2']).exists():
            sql = f'''SELECT * FROM vigilancia_seguimiento ORDER BY dias_sin_acciones DESC;'''
        else:
            sql = f'''SELECT * FROM vigilancia_seguimiento WHERE jefe_cobro = '{user.upper()}' ORDER BY dias_sin_acciones DESC;'''
        
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        queryset = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            queryset.append(dict(rowset))

        context['programacion'] = queryset

        context['plan_pagos'] = Programa.objects.filter(
            detalle_programa__estatus='PLAN DE PAGOS'
            #seguimiento__icontains=user
        ).exclude(
            estatus='CONCLUIDO'
        ).distinct('id')

        context['apoyo_ejecucion'] = Programa.objects.filter(
            detalle_programa__estatus='SOLICITUD ACEPTADA'
            #seguimiento__icontains=user
        ).exclude(
            estatus='CONCLUIDO'
        ).distinct('id')

        total = Pagos.objects.filter(
            programa_id__seguimiento=username,
            fecha__range=['2023-01-01','2023-12-31'],
            is_active=True
        ).aggregate(
            total_recargos=Sum('recargos'), 
            total_accesorios=Sum('accesorios'), 
            total_impuesto=Sum('impuesto')
        )

        if total['total_recargos'] != None:
            recargos = total['total_recargos']
        else:
            recargos = 0

        if total['total_accesorios'] != None:
            accesorios = total['total_accesorios']
        else: 
            accesorios = 0

        if total['total_impuesto'] != None:
            impuesto = total['total_impuesto']
        else:
            impuesto = 0

        context['acumulado'] = recargos + accesorios + impuesto

        return context

def ExportarSeguimiento(request):
    user = request.user.nombres + ' ' + request.user.apellidos
    username = request.user.username

    cursor = connection.cursor()

    if User.objects.filter(username=username, groups__name__in=['DIRECTOR','COORDINACION VIGILANCIA','JEFE COBRO 2']).exists():
        sql = f'''SELECT oficio, rfc, nombre, programa, autorizacion, estatus FROM vigilancia_seguimiento ORDER BY dias_sin_acciones DESC;'''
    else:
        sql = f'''SELECT oficio, rfc, nombre, programa, autorizacion, estatus FROM vigilancia_seguimiento WHERE jefe_cobro = '{user.upper()}' ORDER BY dias_sin_acciones DESC;'''
    
    cursor.execute(sql)

    fieldnames = [name[0] for name in cursor.description]

    queryset = []
    for row in cursor.fetchall():
        row_tmp = list(row)

        rowset = []
        for field in row_tmp:
            rowset.append(field)

        queryset.append(rowset)
    
    return generar_excel_orm(request, "reporte_seguimiento.csv", queryset, fieldnames)

def ExportarPlanPagos(request):
    query = f"""
        SELECT DISTINCT
            substring(pp.folio from 16 for LENGTH(pp.folio)) as folio, pp.rfc, pp.nombre, pp.programa, pp.estatus, TO_CHAR(b.autorizacion, 'dd/mm/YYYY') as autorizacion
        FROM programacion_programa pp 
        LEFT JOIN programacion_detalle pd ON pd.programa_id_id = pp.id
        LEFT JOIN ( 
            SELECT programacion_detalle.programa_id_id,
                max(programacion_detalle.fecha) AS autorizacion
            FROM programacion_detalle
            WHERE ((upper((programacion_detalle.estatus)::text) = 'OFICIO'::text) AND (programacion_detalle.is_active = true))
            GROUP BY programacion_detalle.programa_id_id
            )  b on pp.id = b.programa_id_id
        WHERE pd.estatus = 'PLAN DE PAGOS' AND pp.estatus <> 'CONCLUIDO' AND pd.is_active = true;
    """
    cursor = connection.cursor()
    cursor.execute(query)

    fieldnames = [name[0] for name in cursor.description]

    queryset = []
    for row in cursor.fetchall():
        # Convertimos la trupla a array para poder iterar
        row_tmp = list(row)

        rowset = []
        for field in row_tmp:
            rowset.append(field) 

        queryset.append(rowset)
    
    return generar_excel_orm(request, "reporte_plan_pagos.csv", queryset, fieldnames)


class Lista_Concluidos(GlobalMixin, ListView):
    template_name = 'programacion/lista_concluidos.html'
    model = Programa
    context_object_name = 'concluidos'
    
    def get_queryset(self):

        queryset = Programa.objects.filter(
            estatus='CONCLUIDO', 
            detalle_programa__estatus = 'CONCLUIDO'
            #detalle_programa__fecha__range=['2021-01-01', '2021-12-31']
        ).distinct('id')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(Lista_Concluidos, self).get_context_data(**kwargs)

        if User.objects.filter(username=self.request.user.username, groups__name__contains='DIRECTOR'):
            context['permission'] = 'DIRECTOR'
        else:
            context['permission'] = ''

        return context


class Lista_Transferencias(GlobalMixin, ListView):
    template_name = 'programacion/lista_transferencias.html'
    model = Programa
    context_object_name = 'transferencias'
    
    def get_queryset(self):

        queryset = Programa.objects.filter(
            estatus='TRANSFERIDO', 
            etapa='CIERRE'
        )
            
        return queryset


class Ultimos_Movimientos(GlobalMixin, ListView):
    template_name = 'programacion/consulta/ultimos_movimientos.html'
    model = Programa
    context_object_name = 'programacion'
    
    def get_queryset(self):
    
        cursor = connection.cursor()
        cursor.execute("SELECT movimiento, fecha, rfc, nombre, usuario, comentario, area FROM public.Ultimos_Movimientos ORDER BY FECHA DESC LIMIT 1000")
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))

        queryset = result

        return queryset        


class Admin_Programacion(LoginRequiredMixin, ListView):
    template_name = 'programacion/admin_programacion.html'
    context_object_name = 'programacion'

    def get_data(self, busqueda, rfc, opcion, id_cfdi):

        url = "http://172.31.113.187:180/Informacion_Contribuyente.asmx?op=Obtiene_CFDI"
        headers = {
            'Content-Type': 'text/xml',
            'SOAPAction': 'http://tempuri.org/Obtiene_CFDI'
        }
        xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n  <soap:Body>\r\n    <Obtiene_CFDI xmlns=\"http://tempuri.org/\">\r\n      <BUSQUEDA>" + busqueda + "</BUSQUEDA>\r\n      <rfc>" + rfc + "</rfc>\r\n      <OPCION>" + str(opcion) + "</OPCION>\r\n      <id_cfdi>" + str(id_cfdi) + "</id_cfdi>\r\n      </Obtiene_CFDI>\r\n  </soap:Body>\r\n</soap:Envelope>"
        
        response = requests.post(url, headers=headers, data=xml)
        dictionary = xmltodict.parse(response.text)

        for key, value in dictionary.items():
            for key2, value2 in value.items():
                if key2 == 'soap:Body':
                    for key3, value3 in value2.items():
                        if key3 == 'Obtiene_CFDIResponse':
                            for key4, value4 in value3.items():
                                if key4 == 'Obtiene_CFDIResult':
                                    result = json.loads(value4)

        return result['Table']

    def get_queryset(self):
        programa_id = self.kwargs.get('id')
        return Programa.objects.filter(id=programa_id)


    def get_context_data(self, **kwargs):
        context = super(Admin_Programacion, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')

        obj_Programa = Programa.objects.filter(id=id)

        context['solicitud_aceptada'] = Detalle.objects.filter(
            programa_id = id, 
            is_active=True, 
            estatus__contains='SOLICITUD ACEPTADA'
        ).exists()

        if REC.objects.filter(rfc=obj_Programa[0].rfc).exists():
            obj_REC = REC.objects.filter(rfc=obj_Programa[0].rfc)
            id_contacto = obj_REC[0].id
        else:
            id_contacto = 0

        if Detalle.objects.filter(programa_id = id, estatus__contains='OFICIO').exists():

            if Detalle.objects.filter(programa_id = id, estatus__contains='CONCLUIDO').exists():
                obj_notificado = Detalle.objects.filter(
                    programa_id = id,
                    estatus__contains = 'OFICIO'
                )
                obj_concluido = Detalle.objects.filter(
                    programa_id = id,
                    estatus__contains = 'CONCLUIDO'
                )
                context['fecha_autorizacion'] = obj_notificado
                dias = (obj_concluido[0].fecha - obj_notificado[0].fecha).days
            else:
                today = date.today()

                obj = Detalle.objects.filter(
                    programa_id = id,
                    estatus__contains = 'OFICIO'
                )
                context['fecha_autorizacion'] = obj
                dias = (today - obj[0].fecha).days
        else:
            dias = 0

        context['dias'] = dias
        context['detalles'] = Detalle.objects.filter(
            programa_id=id, 
            is_active=True
        ).exclude(
            estatus__in=['NUEVO','PROPUESTA','FAFD','PRESUNTIVA','OFICIO','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CANCELADA']
        ).order_by('-fecha','-id')  
        
        context['archivos'] = Archivos.objects.filter(
            programa_id=id, 
            is_active=True
        ).order_by('-fecha','-id')

        context['pagos_presuntiva'] = Pagos.objects.filter(
            programa_id=id, 
            presuntiva=True, 
            is_active=True
        ).order_by('-fecha')

        context['pagos'] = Pagos.objects.filter(
            programa_id=id, 
            presuntiva=False, 
            is_active=True
        ).order_by('-fecha')

        context['contactos'] =  Contacto.objects.detalle_all(id_contacto)
        context['edicion'] = obj_Programa[0].estatus

        #context['cfdi'] = self.get_data('', obj_Programa[0].rfc, 3, 0) 

        return context


# ============================= DeleteView ================================================ #

class Eliminar_Archivo(CRUDMixin, DeleteView):
    permission_required = ('delete_archivos')
    
    model = Archivos
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
    permission_required = ('delete_detalle')

    model = Detalle
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
    permission_required = ('delete_pagos')
    
    model = Pagos
    template_name = 'rec/eliminar_datos.html'

    def delete(self, request, *args, **kwargs):
        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            obj_pagos = self.get_object()
            obj_pagos.is_active=False
            obj_pagos.save()

            id = str(obj_pagos.programa_id)

            total = Pagos.objects.filter(
                programa_id=id,
                is_active=True
            ).aggregate(
                total_recargos=Sum('recargos'), 
                total_accesorios=Sum('accesorios'), 
                total_impuesto=Sum('impuesto')
            )
            recaudado = total['total_recargos'] + total['total_accesorios'] + total['total_impuesto']

            instance = Programa.objects.get(pk=id)
            instance.recaudado = recaudado
            instance.save()

            message = 'Pago Eliminado!'
            response = JsonResponse({'message': message})
            return response
        else:
            return reverse_lazy('rec_app:lista-rec')

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

# ============================= UpdateView ================================================ #


class Editar_Detalle(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_detalle')
    
    model = Detalle
    template_name = 'programacion/editar/editar_detalle.html'
    form_class = DetalleForm
    success_message = 'Seguimiento actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Editar_Detalle, self).get_context_data(**kwargs)

        obj = self.get_object()
        selected_etapa = Codigos_Maestros.objects.filter(codigo='XXSTAGE', comentario=obj.etapa)
        context['selected_etapa'] = selected_etapa[0].id
        selected_estatus = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario=obj.estatus)
        context['selected_estatus'] = selected_estatus[0].id

        context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE').exclude(comentario='INTEGRACION')
        context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS').exclude(comentario__in=['CANCELADA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA'])
        
        estatus = Codigos_Maestros.objects.values('id','valor','comentario').filter(codigo='XXSTATUS').exclude(comentario__in=['CANCELADA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CONCLUIDO','TRANSFERIDO','VALIDACION', 'RECHAZADO']).order_by('id')
        context['lista_estatus'] = json.dumps(list(estatus))

        return context

    def get_form_kwargs(self):
        kwargs = super(Editar_Detalle, self).get_form_kwargs()

        obj = Detalle.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id)

        return kwargs

    def form_valid(self, form):        
        estatus = form.cleaned_data['estatus']
        obj = Codigos_Maestros.objects.filter(id=estatus)
        etapa = form.cleaned_data['etapa']
        obj2 = Codigos_Maestros.objects.filter(id=etapa)

        form.instance.usuario = self.request.user.username
        form.instance.etapa = str(obj2[0].comentario)
        form.instance.estatus = str(obj[0].comentario)

        return super(Editar_Detalle, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('programacion_app:admin-programacion', kwargs={'id': self.object.programa_id })


class Editar_Pago(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_pagos')
    
    model = Pagos
    template_name = 'programacion/editar/editar_pagos.html'
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

        obj = Pagos.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id)

        return kwargs

    def get_success_url(self):
        messages.info(self.request, 'pagos')
        return reverse_lazy('programacion_app:admin-programacion', kwargs={'id': self.object.programa_id })

# ============================= CreateView ================================================ #

class Alta_Pagos(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_pagos')
    
    model = Pagos
    template_name = 'programacion/crear/alta_pagos.html'
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
        impuesto = form.cleaned_data['impuesto']
        accesorios = form.cleaned_data['accesorios']
        recargos = form.cleaned_data['recargos']

        if impuesto == '' or impuesto is None:
            impuesto = 0
        if accesorios == '' or accesorios is None:
            accesorios = 0
        if recargos == '' or recargos is None:
            recargos = 0
            
        form.instance.usuario = self.request.user.username
        form.instance.impuesto = impuesto
        form.instance.accesorios = accesorios
        form.instance.recargos = recargos

        return super(Alta_Pagos, self).form_valid(form)

    def get_success_url(self):
        messages.info(self.request, 'pagos')
        return reverse_lazy('programacion_app:admin-programacion', kwargs={'id': self.object.programa_id })


class Alta_Archivos_Solicitud(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_archivos')
    
    model = Archivos
    template_name = 'programacion/crear/alta_archivos_solicitud.html'
    form_class = ArchivosSolicitudForm
    success_message = 'Archivo cargado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Alta_Archivos_Solicitud, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        context['ejercicio'] = Opciones.objects.filter(codigo='SELECT__EJERCICIO').order_by('-valor')
        context['impuestos'] = Codigos_Maestros.objects.filter(codigo='XXTAX').order_by('-valor')

        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Archivos_Solicitud, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):   
        user = self.request.user.username

        instance_ficha = Programa.objects.get(id=self.kwargs['pk'])
        instance_ficha.estatus = 'SOLICITAR APOYO'
        instance_ficha.save()

        Detalle.objects.create(
            programa_id=instance_ficha,
            fecha=date.today(),
            comentarios=form.cleaned_data['comentarios'],
            etapa='SEGUIMIENTO',
            estatus='SOLICITAR APOYO',
            usuario=user
        )

        form.instance.usuario = user

        return super(Alta_Archivos_Solicitud, self).form_valid(form)

    def get_success_url(self):
        messages.info(self.request, 'archivos')
        return self.request.META['HTTP_REFERER']


class Alta_Archivos2(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_archivos')
    
    model = Archivos
    template_name = 'programacion/crear/alta_archivos.html'
    form_class = ArchivosForm2
    success_message = 'Archivo cargado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Alta_Archivos2, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']
        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Archivos2, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user.username

        return super(Alta_Archivos2, self).form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Alta_Archivos(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_archivos')
    
    model = Archivos
    template_name = 'programacion/crear/alta_archivos.html'
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
        # impuesto = form.cleaned_data['impuesto']
        # accesorios = form.cleaned_data['accesorios']
        # recargos = form.cleaned_data['recargos']

        # if impuesto == '' or impuesto is None:
            # impuesto = 0
        # if accesorios == '' or accesorios is None:
            # accesorios = 0
        # if recargos == '' or recargos is None:
            # recargos = 0
            
        form.instance.usuario = self.request.user.username
        # form.instance.impuesto = impuesto
        # form.instance.accesorios = accesorios
        # form.instance.recargos = recargos

        return super(Alta_Archivos, self).form_valid(form)

    def get_success_url(self):
        messages.info(self.request, 'archivos')

        user = self.request.user.username

        redirect = User.objects.filter(username=user, groups__name__in=['COORDINACION PROGRAMACION','COORDINACION VIGILANCIA', 'EJECUTIVO ANALISIS']).exists()

        if redirect:
            return reverse_lazy('programacion_app:autorizacion')
        else:
            return reverse_lazy('programacion_app:admin-programacion', kwargs={'id': self.object.programa_id })


class Alta_Programacion(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_programa')
    
    model = Programa
    template_name = 'programacion/crear/alta_programacion.html'
    form_class = ProgramacionForm
    success_url = reverse_lazy('programacion_app:lista-programacion')
    success_message = 'Folio creado exitosamente!'

    def form_valid(self, form):
        form.instance.usuario = self.request.user.username
        form.instance.estatus = 'VALIDACION'
        
        seguimiento = form.cleaned_data['seguimiento']
        start = str(seguimiento).find('(') + 1
        end = str(seguimiento).find(')')

        form.instance.seguimiento = str(seguimiento)[start:end]

        return super(Alta_Programacion, self).form_valid(form)


class Alta_Solicitud(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Detalle
    template_name = 'programacion/crear/alta_solicitud.html'
    form_class = SolicitarForm
    success_message = 'Solicitud Creada exitosamente!'
    
    def get_context_data(self, **kwargs):
        context = super(Alta_Solicitud, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Solicitud, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        
        return kwargs

    def form_valid(self, form):
        id = form.cleaned_data.get('programa_id')
                
        instance = Programa.objects.get(id = str(id))
        instance.estatus = 'SOLICITUD'
        instance.save()
            
        form.instance.usuario = self.request.user.username
        form.instance.etapa = 'SEGUIMIENTO'
        form.instance.estatus = 'SOLICITUD'
        
        return super(Alta_Solicitud, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('programacion_app:autorizacion')


class Alta_Cierre(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Detalle
    template_name = 'programacion/crear/alta_cierre.html'
    form_class = CierreForm
    success_message = 'Cerrado exitosamente!'
    
    def get_context_data(self, **kwargs):
        context = super(Alta_Cierre, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Cierre, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        
        return kwargs

    def form_valid(self, form):
        id = form.cleaned_data.get('programa_id')
        
        estatus = form.cleaned_data['estatus']
        
        if str(estatus) == 'SOLICITAR APOYO':
            instance = Programa.objects.get(id = str(id))
            instance.estatus = 'SOLICITUD'
            instance.save()
            
            form.instance.usuario = self.request.user.username
            form.instance.etapa = 'SEGUIMIENTO'
            form.instance.estatus = 'SOLICITUD'
            form.instance.comentarios_area = ''
            
        else:
            instance = Programa.objects.get(id = str(id))
            instance.etapa = 'CIERRE'
            instance.estatus = str(estatus)
            instance.save()
            
            form.instance.usuario = self.request.user.username
            form.instance.etapa = 'CIERRE'
            form.instance.estatus = str(estatus)
            form.instance.comentarios_area = ''
        
        return super(Alta_Cierre, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('programacion_app:autorizacion')


class Alta_Detalle(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_detalle')
    
    model = Detalle
    template_name = 'programacion/crear/alta_detalle.html'
    form_class = DetalleForm
    success_message = 'Guardado Exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Alta_Detalle, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='EJECUTIVO ANALISIS').exists():
            context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE', comentario__in=['INTEGRACION'])
            context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario__in=['CANCELADA'])
        elif User.objects.filter(username=user, groups__name__contains='COORDINACION PROGRAMACION').exists():
            context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE', comentario__in=['INTEGRACION'])
            context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario__in=['CANCELADA','1-RECHAZADA','INFORMATIVAS'])
        elif User.objects.filter(username=user, groups__name__contains='COORDINACION VIGILANCIA').exists():

            if 'admin-programacion' in str(self.request.META['HTTP_REFERER']):
                context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE').exclude(comentario='INTEGRACION').order_by('valor')
                context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS').exclude(comentario__in=['CANCELADA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CONCLUIDO','TRANSFERIDO','VALIDACION', 'RECHAZADO']).order_by('id')
            else:
                context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE', comentario__in=['INTEGRACION'])
                context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario__in=['2-RECHAZADA','CONCLUIDO','TRANSFERIDO','RECHAZADO'])
        elif User.objects.filter(username=user, groups__name__contains='DIRECTOR').exists():

            if 'lista-transferencias' in str(self.request.META['HTTP_REFERER']):
                context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE', comentario__in=['INTEGRACION'])
                context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario__in=['RECHAZADO'])
            else:
                context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE', comentario__in=['INTEGRACION'])
                context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario__in=['CANCELADA','3-RECHAZADA'])
        elif User.objects.filter(username=user, groups__name__contains='EJECUCION').exists():
            context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE', comentario__in=['SEGUIMIENTO'])
            context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario__in=['RECHAZADO'])

        else:
            context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE').exclude(comentario='INTEGRACION').order_by('valor')
            context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS').exclude(comentario__in=['CANCELADA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CONCLUIDO','TRANSFERIDO','VALIDACION', 'RECHAZADO']).order_by('id')

            estatus = Codigos_Maestros.objects.values('id','valor','comentario').filter(codigo='XXSTATUS').exclude(comentario__in=['CANCELADA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CONCLUIDO','TRANSFERIDO','VALIDACION', 'RECHAZADO']).order_by('id')
            context['lista_estatus'] = json.dumps(list(estatus))
        
        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Detalle, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        
        return kwargs

    def form_valid(self, form):
        id = form.cleaned_data.get('programa_id')
        
        estatus = form.cleaned_data['estatus']
        obj = Codigos_Maestros.objects.filter(id=estatus)
        etapa = form.cleaned_data['etapa']
        obj2 = Codigos_Maestros.objects.filter(id=etapa)
        
        if str(obj[0].comentario) == 'PERSONAL' or str(obj[0].comentario) == 'POR CORREO':
            stage = 'NOTIFICADO'
        elif str(obj[0].comentario) == 'PRESENCIAL' or str(obj[0].comentario) == 'VIRTUAL':
            stage = 'ENTREVISTA'
        else:
            stage = str(obj[0].comentario)

        instance = Programa.objects.get(id = str(id))
        instance.etapa = str(obj2[0].comentario)
        instance.estatus = stage
        instance.save()

        form.instance.usuario = self.request.user.username
        form.instance.etapa = str(obj2[0].comentario)
        form.instance.estatus = str(obj[0].comentario)

        return super(Alta_Detalle, self).form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Cierre_Apoyo(CRUDMixin, SuccessMessageMixin, TemplateView):
    permission_required = ('add_detalle')
    #model = Detalle
    template_name = 'programacion/crear/cierre_apoyo.html'
    success_message = 'Cerrado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Cierre_Apoyo, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        context['form'] = CerrarApoyoForm    
        
        return context

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']
        
        instance = Programa.objects.get(id = str(id))
        instance.estatus = 'SOLICITUD CONCLUIDA'
        instance.save()

        Detalle.objects.create(
            programa_id=instance,
            fecha=date.today(),
            comentarios=request.POST['comentarios'],
            estatus='SOLICITUD CONCLUIDA',
            usuario=self.request.user.username
        )

        return redirect(self.request.META['HTTP_REFERER'])

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class EstatusCierreView(LoginRequiredMixin, TemplateView):
    template_name = 'programacion/crear/estatus_cierre.html'

    def get_context_data(self, **kwargs):
        context = super(EstatusCierreView, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        context['form'] = EstatusCierre    
        
        return context

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']

        estatus = Codigos_Maestros.objects.filter(id=str(request.POST['estatus']))
        estatus_cierre = Codigos_Maestros.objects.filter(id=str(request.POST['estatus_cierre']))

        instance = Programa.objects.get(id = str(id))
        instance.estatus = estatus[0].comentario
        instance.save()

        Detalle.objects.create(
            programa_id=instance,
            fecha=date.today(),
            comentarios=request.POST['comentarios'],
            estatus=estatus_cierre[0].comentario,
            usuario=self.request.user.username
        )

        Detalle.objects.create(
            programa_id=instance,
            fecha=date.today(),
            comentarios='',
            estatus=estatus[0].comentario,
            usuario=self.request.user.username
        )

        messages.info(self.request, 'por_cerrar')

        return redirect(self.request.META['HTTP_REFERER'])

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class CerrarRFCView(LoginRequiredMixin, TemplateView):
    template_name = 'programacion/crear/cerrar_rfc.html'

    def get_context_data(self, **kwargs):
        context = super(CerrarRFCView, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        context['form'] = CerrarRFCForm    
        
        return context

    def post(self, request, *args, **kwargs):
        FormData = request.POST
        id = self.kwargs['pk']

        instance = Programa.objects.get(id = str(id))

        if 'cerrar' in FormData:
            if FormData['cerrar'] == 'on':
                instance.is_close = True

                Detalle.objects.create(
                    programa_id=instance,
                    fecha=date.today(),
                    comentarios=request.POST['comentarios'],
                    estatus='CERRADO',
                    usuario=self.request.user.username
                )
        
        if 'reactivar' in FormData:
            if FormData['reactivar'] == 'on':
                instance.estatus = 'REACTIVADO'

                Detalle.objects.create(
                    programa_id=instance,
                    fecha=date.today(),
                    comentarios=request.POST['comentarios'],
                    estatus='REACTIVADO',
                    usuario=self.request.user.username
                )

        instance.save()

        return redirect(self.request.META['HTTP_REFERER'])

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']     

# ============================= Views ================================================ #

class Ver_Programacion(LoginRequiredMixin, DetailView):
    model = Programa
    template_name = 'programacion/consulta/ver_programacion.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Programacion, self).get_context_data(**kwargs)
        context['detalles'] = Detalle.objects.filter(programa_id=self.kwargs.get('pk'))    
        
        return context 


class Ver_Archivos(LoginRequiredMixin, DetailView):
    model = Programa
    template_name = 'programacion/consulta/ver_archivos.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Archivos, self).get_context_data(**kwargs)
        context['archivos'] = Archivos.objects.filter(programa_id=self.kwargs.get('pk'))    
        
        return context


class Ver_Pagos(LoginRequiredMixin, DetailView):
    model = Programa
    template_name = 'programacion/consulta/ver_pagos.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Pagos, self).get_context_data(**kwargs)
        id = self.kwargs.get('pk')

        context['pagos_presuntiva'] = Pagos.objects.filter(programa_id = id, presuntiva=True)      
        context['pagos'] = Pagos.objects.filter(programa_id = id, presuntiva=False)       
                
        return context


class Ver_Reporte_2(LoginRequiredMixin, ListView):
    template_name = 'programacion/consulta/ver_reporte_2.html'
    context_object_name = 'programacion'

    def get_queryset(self):
        id = self.kwargs.get('pk')

        queryset = Programa.objects.filter(id=id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Ver_Reporte_2, self).get_context_data(**kwargs)
        id = self.kwargs.get('pk')

        obj_Programa = Programa.objects.filter(id=id)

        if REC.objects.filter(rfc=obj_Programa[0].rfc).exists():
            obj_REC = REC.objects.filter(rfc=obj_Programa[0].rfc)
            id_contacto = obj_REC[0].id
        else:
            id_contacto = 0

        if Detalle.objects.filter(programa_id=id, estatus__contains='OFICIO').exists():

            if Detalle.objects.filter(programa_id=id, estatus__contains='CONCLUIDO').exists():
                obj_notificado = Detalle.objects.filter(
                    programa_id=id,
                    estatus__contains='OFICIO'
                )
                obj_concluido = Detalle.objects.filter(
                    programa_id=id,
                    estatus__contains='CONCLUIDO'
                )
                dias = (obj_concluido[0].fecha - obj_notificado[0].fecha).days
            else:
                today = date.today()

                obj = Detalle.objects.filter(
                    programa_id=id,
                    estatus__contains='OFICIO'
                )
                dias = (today - obj[0].fecha).days
        else:
            dias = 0

        context['dias'] = dias

        context['detalles'] = Detalle.objects.filter(
            programa_id=id, 
            is_active=True
        ).exclude(
            estatus__in=['FAFD','NUEVO','PROPUESTA','PRESUNTIVA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CANCELADA']
        ).order_by('fecha')

        context['archivos'] = Archivos.objects.filter(programa_id=id, is_active=True)
        context['pagos_presuntiva'] = Pagos.objects.filter(
            programa_id=id, presuntiva=True, is_active=True)
        context['pagos'] = Pagos.objects.filter(
            programa_id=id, presuntiva=False, is_active=True)
        context['contactos'] = Contacto.objects.detalle_all(id_contacto)
        return context


class Ver_Reporte(LoginRequiredMixin, ListView):
    template_name = 'programacion/consulta/ver_reporte.html'
    context_object_name = 'programacion'

    def get_queryset(self):
        id = self.kwargs.get('pk')

        queryset = Programa.objects.filter(id = id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Ver_Reporte, self).get_context_data(**kwargs)
        id = self.kwargs.get('pk')

        obj_Programa = Programa.objects.filter(id=id)

        if REC.objects.filter(rfc=obj_Programa[0].rfc).exists():
            obj_REC = REC.objects.filter(rfc=obj_Programa[0].rfc)
            id_contacto = obj_REC[0].id
        else:
            id_contacto = 0

        if Detalle.objects.filter(programa_id = id, estatus__contains='OFICIO').exists():

            if Detalle.objects.filter(programa_id = id, estatus__contains='CONCLUIDO').exists():
                obj_notificado = Detalle.objects.filter(
                    programa_id = id,
                    estatus__contains = 'OFICIO'
                )
                obj_concluido = Detalle.objects.filter(
                    programa_id = id,
                    estatus__contains = 'CONCLUIDO'
                )
                context['fecha_autorizacion'] = obj_notificado
                dias = (obj_concluido[0].fecha - obj_notificado[0].fecha).days
            else:
                today = date.today()

                obj = Detalle.objects.filter(
                    programa_id = id,
                    estatus__contains = 'OFICIO'
                )
                context['fecha_autorizacion'] = obj
                dias = (today - obj[0].fecha).days
        else:
            dias = 0

        context['dias'] = dias
        context['detalles'] = Detalle.objects.filter(
            programa_id = id, 
            is_active=True
        ).exclude(
            estatus__in=['FAFD','NUEVO','PROPUESTA','PRESUNTIVA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CANCELADA']  
        ).order_by('fecha')  
        
        context['archivos'] = Archivos.objects.filter(programa_id = id, is_active=True)    
        context['pagos_presuntiva'] = Pagos.objects.filter(programa_id = id, presuntiva=True, is_active=True)      
        context['pagos'] = Pagos.objects.filter(programa_id = id, presuntiva=False, is_active=True)    
        context['contactos'] =  Contacto.objects.detalle_all(id_contacto)
        return context


class Ver_Todo(LoginRequiredMixin, DetailView):
    model = Programa
    template_name = 'programacion/consulta/ver_todo.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Todo, self).get_context_data(**kwargs)
        id = self.kwargs.get('pk')
      
        context['detalles'] = Detalle.objects.filter(
            programa_id = id, 
            is_active=True
        ).exclude(
            estatus__in=['NUEVO','PROPUESTA','FAFD','PRESUNTIVA','OFICIO','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CANCELADA']
        ).order_by('-fecha','-id')  

        context['archivos'] = Archivos.objects.filter(
            programa_id = id, 
            is_active=True
        ).order_by('-fecha','-id')  

        context['pagos_presuntiva'] = Pagos.objects.filter(
            programa_id = id, 
            presuntiva=True, 
            is_active=True
        ).order_by('-fecha')

        context['pagos'] = Pagos.objects.filter(
            programa_id = id,
            presuntiva=False, 
            is_active=True
        ).order_by('-fecha')

        return context

#----------------------------------------------- AUTORIZACION -------------------------------------------------#

class Lista_Autorizacion(GlobalMixin, ListView):
    template_name = 'programacion/lista_autorizacion.html'
    model = Programa
    context_object_name = 'programacion'
    
    def get_context_data(self, **kwargs):
        context = super(Lista_Autorizacion, self).get_context_data(**kwargs)

        user = self.request.user.username

        if User.objects.filter(username=user, groups__name__contains='EJECUTIVO ANALISIS'):
            context['permission'] = 'EJECUTIVO ANALISIS'
            
        elif User.objects.filter(username=user, groups__name__contains='COORDINACION PROGRAMACION'):
            context['permission'] = 'COORDINACION PROGRAMACION'
            
        elif User.objects.filter(username=user, groups__name__contains='COORDINACION VIGILANCIA'):
            context['permission'] = 'COORDINACION VIGILANCIA'
            
        elif User.objects.filter(username=user, groups__name__contains='DIRECTOR'):
            context['permission'] = 'DIRECTOR'
        
        cursor = connection.cursor()
        sql = f'''select  
                    folio,
                    rfc,
                    substring(folio,16,6) consecutivo,
                    substring(folio,23,4) ejercicio
                from programacion_programa 
                    where folio <> '' 
                order by  
                    ejercicio desc, 
                    consecutivo desc
                limit 1'''
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))

        context['last_folio'] = result
            
        # context['revision'] = Programa.objects.filter(estatus__in=['NUEVO','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','PROPUESTA','FAFD','OFICIO','PRESUNTIVA'])
        # Se quito la vista del estatus de oficio para el listado de revisión 2023/04/21
        context['revision'] = Programa.objects.filter(estatus__in=['NUEVO','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','PROPUESTA','FAFD','PRESUNTIVA'])
        # Se quito la vista del estatus de oficio para el listado de revisión 2023/04/21
        context['por_cerrar'] = Programa.objects.filter(estatus__in=['PAGO TOTAL','PARA TRANSFERIR', 'RECHAZADO', 'ACLARACION'])
        context['solicitar_apoyo'] = Programa.objects.filter(estatus__in=['SOLICITAR APOYO'])
        
        context['reasignar'] = Programa.objects.all().exclude(estatus__in=['NUEVO','CANCELADA','PROPUESTA','PRESUNTIVA','FAFD','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','OFICIO','CONCLUIDO','TRANSFERIDO','INFORMATIVAS'])
            
        context['canceladas'] = Programa.objects.filter(
            estatus__in=['CANCELADA'], 
            fecha__range=['2023-01-01','2023-12-31']
        )

        impuestos = Impuestos.objects.values(
            'contribuyente'
        ).annotate(
            impuestos=ArrayAgg('impuesto__comentario', distinct=True)
        ).filter(
            Q(ejercicio = 1) | Q(ejercicio_1 = 1) | Q(ejercicio_2 = 1) | Q(ejercicio_3 = 1) | Q(ejercicio_4 = 1) | Q(ejercicio_5 = 1),
            contribuyente=OuterRef('pk')
        ).order_by()

        context['en_proceso'] = Contribuyentes.objects.filter(
            ~Q(estatus=None),
            usuario = user, 
            is_ready = False
        ).annotate(
            impuestos=Subquery(impuestos.values('impuestos')[:1])
        )

        elements = [1, 2, 3, 4, 5]
        elements_query = []
        elements_count = context['en_proceso'].count()
        if elements_count < 6: 
            while elements_count > 0 :
                elements_query.append(elements_count)
                elements.remove(elements_count)
                elements_count -= 1                
        else:
            elements = None
        context['rango'] = elements
       
        return context
        
    def get_queryset(self):
        user = self.request.user.username
        if User.objects.filter(username=user, groups__name__contains='EJECUTIVO ANALISIS'):
            return Programa.objects.filter(usuario=user, estatus__in=['NUEVO','1-RECHAZADA','PROPUESTA','2-RECHAZADA'])

        elif User.objects.filter(username=user, groups__name__contains='COORDINACION PROGRAMACION'):
            return Programa.objects.filter(estatus__in=['PROPUESTA','2-RECHAZADA'])

        elif User.objects.filter(username=user, groups__name__contains='COORDINACION VIGILANCIA'):
            return Programa.objects.filter(estatus__in=['FAFD','OFICIO','3-RECHAZADA','REACTIVADO'])

        elif User.objects.filter(username=user, groups__name__contains='DIRECTOR'):
            return Programa.objects.filter(estatus__in=['PRESUNTIVA'])

class Agregar_Contribuyente(CreateView):
    model = Contribuyentes
    template_name = 'programacion/crear/agrega_contribuyente_manual.html'
    success_url = reverse_lazy('programacion_app:autorizacion')
    fields = ['rfc','modelo','prioridad','programa','fecha_inicio','estatus','usuario']
    def get_context_data(self, **kwargs):
        context = super(Agregar_Contribuyente, self).get_context_data(**kwargs)
        context['usuario'] = self.request.user.username
        context['hoy'] = date.today().strftime("%d/%m/%Y")
        return context

class Alta_Contribuyente(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_programa')
    
    model = Programa
    template_name = 'programacion/crear/alta_contribuyente.html'
    form_class = ContribuyenteForm
    success_url = reverse_lazy('programacion_app:autorizacion')

    def form_valid(self, form):

        Contribuyentes.objects.filter(
            usuario=self.request.user.username,
            rfc=form.cleaned_data['rfc'],
            is_ready=False
        ).update(is_ready=True)

        form.instance.rfc = form.cleaned_data['rfc']
        form.instance.fecha = date.today()
        form.instance.folio = ''
        form.instance.usuario = self.request.user.username
        form.instance.seguimiento = ''
        form.instance.etapa = 'INTEGRACION'
        form.instance.estatus = 'NUEVO'

        return super(Alta_Contribuyente, self).form_valid(form)


class Editar_Archivo_Solicitud(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_archivos')
    
    model = Archivos
    template_name = 'programacion/editar/editar_archivos_solicitud.html'
    form_class = ArchivosForm
    success_message = 'Archivo actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Editar_Archivo_Solicitud, self).get_context_data(**kwargs)

        obj = self.get_object()
        selected_tipo = Codigos_Maestros.objects.filter(comentario=obj.tipo)
        context['selected_tipo'] = selected_tipo[0].id

        context['ejercicio'] = Opciones.objects.filter(codigo='SELECT__EJERCICIO').order_by('-valor')
        context['impuestos'] = Codigos_Maestros.objects.filter(codigo='XXTAX').order_by('-valor')
        
        return context

    def get_form_kwargs(self):
        kwargs = super(Editar_Archivo_Solicitud, self).get_form_kwargs()

        obj = Archivos.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id)

        return kwargs 

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Editar_Archivo(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_archivos')
    
    model = Archivos
    template_name = 'programacion/editar/editar_archivos.html'
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

        obj = Archivos.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id)

        return kwargs

    def form_valid(self, form):        
        tipo = form.cleaned_data['tipo']
        if str(tipo) == 'REQUERIMIENTO':
            obj = self.get_object()
            instance_ficha = Programa.objects.get(id=str(obj.programa_id))
            instance_ficha.estatus = 'SOLICITAR APOYO'
            instance_ficha.save()

            Detalle.objects.create(
                programa_id=instance_ficha,
                fecha=date.today(),
                comentarios='',
                etapa='SEGUIMIENTO',
                estatus='SOLICITAR APOYO',
                usuario=self.request.user.username
            )

        return super(Editar_Archivo, self).form_valid(form)

    def get_success_url(self):
        messages.info(self.request, 'archivos')

        if User.objects.filter(username=self.request.user.username, groups__name__contains = 'VIGILANCIA').exists():
            return reverse_lazy('programacion_app:admin-programacion', kwargs={'id': self.object.programa_id_id })
        else:
            return reverse_lazy('programacion_app:autorizacion')


class Editar_Contribuyente(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_programa')
    
    model = Programa
    template_name = 'programacion/editar/editar_contribuyente.html'
    form_class = ContribuyenteForm

    def get_context_data(self, **kwargs):
        context = super(Editar_Contribuyente, self).get_context_data(**kwargs)

        obj = self.get_object()
        selected_program = Codigos_Maestros.objects.filter(comentario=obj.programa)
        context['selected_program'] = selected_program[0].id

        return context  

    def get_success_url(self):
        return reverse_lazy('programacion_app:autorizacion')


class Get_Contribuyente(ListView):

    model = REC
    template_name = 'programacion/consulta/ver_contribuyente.html'

    def get_queryset(self):
        #return REC.objects.filter(rfc=self.kwargs.get('rfc')).values_list('nombre', 'direccion')
        return REC.objects.filter(rfc__icontains=self.kwargs.get('rfc'))


    def get(self, request, *args, **kwargs):

        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = serialize('json', self.get_queryset())

            # print(data)

            # lista_rec = []
            # for data in self.get_queryset():
            #     data_rec = {}
            #     data_rec['nombre'] = data.nombre
            #     data_rec['direccion'] = data.direccion
            #     lista_rec.append(data_rec)

            # data = json.dumps(lista_rec)

            
            #print(data)
            
            return HttpResponse(data, 'application/json')
        else:
            return render(request, self.template_name)


class Ver_Autorizacion(LoginRequiredMixin, DetailView):
    model = Programa
    template_name = 'programacion/consulta/ver_autorizacion.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Autorizacion, self).get_context_data(**kwargs)
        id = self.kwargs.get('pk')
      
        context['detalles'] = Detalle.objects.filter(
            programa_id = id, 
            is_active=True
        ).exclude(
            estatus__in=['NUEVO','ENTREGADO','NOTIFICADO','NO LOCALIZADO','ENTREVISTA','NO ASISTIO','REPROGRAMACION','SEGUIMIENTO','ACLARACION','PAGO PARCIAL','PAGO TOTAL','CONCLUIDO','TRANSFERIDO','VALIDACION']
        ).order_by('-fecha','-id')

        context['archivos'] = Archivos.objects.filter(
            programa_id = id, 
            is_active=True
        ).order_by('-fecha','-id')    
       
        return context


class Asignar(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "programacion/asignar.html"
    success_url = reverse_lazy('programacion_app:autorizacion')
    form_class = AsignarForm
    success_message = "Propuestas publicadas correctamente!"

    def form_valid(self, form):
        seguimiento = form.cleaned_data['seguimiento']
        start = str(seguimiento).find('(') + 1
        end = str(seguimiento).find(')')   

        if form.cleaned_data['lista']:
            list_id = form.cleaned_data['lista'].split(',')
            user = self.request.user.username
            cmmt = form.cleaned_data['observaciones']

            def get_folio():
                #query = Programa.objects.all().exclude(
                #    folio=''
                #).order_by('-id')[:1]
                
                cursor = connection.cursor()
                sql = f'''select  
                            folio,
                            substring(folio,16,6) consecutivo,
                            substring(folio,23,4) ejercicio
                        from programacion_programa 
                            where folio <> '' 
                        order by  
                            ejercicio desc, 
                            consecutivo desc
                        limit 1'''
                cursor.execute(sql)
                fieldnames = [name[0] for name in cursor.description]
                result = []
                for row in cursor.fetchall():
                    rowset = []
                    for field in zip(fieldnames, row):
                        rowset.append(field)
                    result.append(dict(rowset))

                query = result

                query_id = str(query[0]['consecutivo'])
                query_year = str(query[0]['ejercicio'])
                
                year = date.today().year
                
                if year == int(query_year):
                    new_id = int(str(query_id)) + 1
                else:
                    new_id = 1
                    
                folio = 'SATEG-03-02-01-' + str(new_id).zfill(6) + '/' + str(year)

                return folio


            if User.objects.filter(username=user, groups__name__contains='EJECUTIVO ANALISIS'):
                Programa.objects.filter(id__in=list_id).update(estatus='PROPUESTA')

                for id in list_id:
                    instance = Programa.objects.get(pk=id)
                    Detalle.objects.create(
                        programa_id=instance,
                        fecha=date.today(),
                        comentarios=cmmt,
                        estatus='PROPUESTA',
                        usuario=user
                    )

                    instance_rec_notificados = REC_Notificados.objects.filter(rfc__contains=instance.rfc)
                    if instance_rec_notificados:
                        for rec_noti in instance_rec_notificados:
                            instance_rec_notificado = REC_Notificados.objects.get(pk=rec_noti.id)
                            instance_rec_notificado.direccion = instance.direccion
                            instance_rec_notificado.save()
                    else:
                        REC_Notificados.objects.create(
                            rfc=instance.rfc,
                            nombre=instance.nombre,
                            direccion=instance.direccion
                        )

                    instances_rec = REC.objects.filter(rfc__contains=instance.rfc)
                    if instances_rec:
                        for rec in instances_rec:
                            instance_rec = REC.objects.get(pk=rec.id)
                            instance_rec.direccion = instance.direccion
                            instance_rec.save()
                    else:
                        REC.objects.create(
                            rfc=instance.rfc,
                            nombre=instance.nombre,
                            direccion=instance.direccion,
                            fecha_alta=date.today()
                        )
            elif User.objects.filter(username=user, groups__name__contains='COORDINACION PROGRAMACION'):
                Programa.objects.filter(id__in=list_id).update(estatus='FAFD')

                for id in list_id:
                    instance = Programa.objects.get(pk=id)
                    Detalle.objects.create(
                        programa_id=instance,
                        fecha=date.today(),
                        comentarios=cmmt,
                        estatus='FAFD',
                        usuario=user
                    )


            elif User.objects.filter(username=user, groups__name__contains='COORDINACION VIGILANCIA'):
                for id in list_id:
                    if Programa.objects.filter(pk=id, estatus='FAFD').exists():
                        instance = Programa.objects.get(pk=id)
                        Detalle.objects.create(
                            programa_id=instance,
                            fecha=date.today(),
                            comentarios=cmmt,
                            estatus='PRESUNTIVA',
                            usuario=user
                        )
                        
                for id in list_id:
                    if Programa.objects.filter(pk=id, estatus='3-RECHAZADA').exists():
                        instance = Programa.objects.get(pk=id)
                        instance.estatus = 'PRESUNTIVA'
                        instance.save()

                        Detalle.objects.create(
                            programa_id=instance,
                            fecha=date.today(),
                            comentarios=cmmt,
                            estatus='PRESUNTIVA',
                            usuario=user
                        )
                        
                for id in list_id:
                    if Programa.objects.filter(pk=id, estatus='OFICIO').exists():
                        instance = Programa.objects.get(pk=id)
                        Detalle.objects.create(
                            programa_id=instance,
                            fecha=date.today(),
                            comentarios='Presuntiva Determinada',
                            estatus='VALIDACION',
                            usuario='gcisnerosg'
                        )

                Programa.objects.filter(id__in=list_id, estatus='FAFD').update(estatus='PRESUNTIVA')
                Programa.objects.filter(id__in=list_id, estatus='OFICIO').update(seguimiento=str(seguimiento)[start:end], etapa='SEGUIMIENTO', estatus='VALIDACION')
                
                #Programa.objects.filter(id__in=list_id).update(seguimiento=str(seguimiento)[start:end])

            elif User.objects.filter(username=user, groups__name__contains='DIRECTOR'):
                Programa.objects.filter(id__in=list_id).update(estatus='OFICIO')
                
                for id in list_id:
                    instance = Programa.objects.get(pk=id)
                    folio = get_folio()
                    instance.folio = folio
                    instance.save()
                    
                    #self.request.session['folio'] = folio

                    Detalle.objects.create(
                        programa_id=instance,
                        fecha=date.today(),
                        comentarios=cmmt,
                        estatus='OFICIO',
                        usuario=user
                    )


        return super(Asignar, self).form_valid(form)


class Reasignar(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "programacion/reasignar.html"
    success_url = reverse_lazy('programacion_app:autorizacion')
    form_class = ReasignarForm
    success_message = "Reasignado correctamente!"

    def form_valid(self, form):
        seguimiento = form.cleaned_data['seguimiento']
        start = str(seguimiento).find('(') + 1
        end = str(seguimiento).find(')')

        if form.cleaned_data['lista']:
            list_id = form.cleaned_data['lista']
            user = self.request.user.username

            if User.objects.filter(username=user, groups__name__contains='COORDINACION VIGILANCIA'):

                obj = Programa.objects.get(id=str(list_id))
                obj_user = User.objects.get(username=obj.seguimiento)

                cmmt = 'De: ' + str(obj_user.nombres) + ' ' + str(obj_user.apellidos) + ' (' + str(obj_user.username) + ')' + \
                    ' A: ' + str(seguimiento)

                Detalle.objects.create(
                    programa_id=obj,
                    fecha=date.today(),
                    comentarios=cmmt,
                    estatus='REASIGNADO',
                    usuario=self.request.user.username
                )
                
                Programa.objects.filter(
                    id=list_id
                ).update(
                    estatus='REASIGNADO',
                    seguimiento=str(seguimiento)[start:end]
                )

        return super(Reasignar, self).form_valid(form)


class Elegir_Contribuyente(LoginRequiredMixin, TemplateView):
    template_name = 'programacion/editar/elegir.html'

    def get_context_data(self, **kwargs):
        context = super(Elegir_Contribuyente, self).get_context_data(**kwargs)

        auditoria_rfcs = Programa_Transferidos.objects.filter(
            ~Q(usuario=''),
            area = 'AUDITORIA',
            is_active = True,
            estatus__in = ['ACEPTADO','ACTIVO','CIERRE']
        ).values('rfc')

        vigilancia_rfcs = Programa.objects.all().exclude(
            estatus__in = ['CONCLUIDO']
        ).values('rfc')

        queryset = Contribuyentes.objects.filter(
            usuario = None
        ).order_by(
            'prioridad'
        ).exclude(
            rfc__in = auditoria_rfcs
        ).exclude(
            rfc__in = vigilancia_rfcs
        ).first()

        if queryset:
            context['modelos'] = queryset.modelo

            data = {
                "rfc": queryset.rfc,
                "programa": queryset.programa
            }

            context['pk'] = queryset.id
        else:
            data = {
                "rfc": 'No Hay RFCs',
                "programa": 'No Hay RFCs'
            }

            context['pk'] = 0

        context['form'] = ContribuyentesForm(data)
        
        return context

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']
        
        instance = Contribuyentes.objects.get(id = str(id))
        instance.usuario = self.request.user.username
        instance.estatus = 'EN PROCESO'
        instance.fecha_inicio = date.today()
        instance.save()

        messages.info(self.request, 'en_proceso')

        return redirect(self.request.META['HTTP_REFERER'])


class ImpuestosView(LoginRequiredMixin, TemplateView):
    template_name = 'programacion/editar/impuestos.html'

    def get_context_data(self, **kwargs):
        context = super(ImpuestosView, self).get_context_data(**kwargs)

        context['form'] = ImpuestosForm
        context['impuestos'] = Codigos_Maestros.objects.filter(codigo='XXTAX')
        
        return context


class Admin_Impuestos(View):

    def post(self, request, *args, **kwargs):

        contribuyente = self.kwargs.get('rfc')

        # Convertir data a Diccionario de python
        formData = ast.literal_eval(request.POST['data'])

        with transaction.atomic():
            for value in formData:
                Impuestos.objects.filter(
                    pk=value['id']
                ).update(
                    ejercicio = int(value['ejercicio']),
                    ejercicio_1 = int(value['ejercicio_1']),
                    ejercicio_2 = int(value['ejercicio_2']),
                    ejercicio_3 = int(value['ejercicio_3']),
                    ejercicio_4 = int(value['ejercicio_4']),
                    ejercicio_5 = int(value['ejercicio_5'])
                )

        messages.info(self.request, 'en_proceso')
        messages.success(self.request, 'Impuesto Cargado Exitosamente!')

        # Limpiar impuestos con 0
        impuestos = Impuestos.objects.values(
            'contribuyente'
        ).annotate(
            impuestos=ArrayAgg('impuesto', distinct=True)
        ).filter(
            Q(ejercicio = 1) | Q(ejercicio_1 = 1) | Q(ejercicio_2 = 1) | Q(ejercicio_3 = 1) | Q(ejercicio_4 = 1) | Q(ejercicio_5 = 1),
            contribuyente=contribuyente
        ).order_by()

        # impuestos = {'contribuyente': 32, 'impuestos': [20, 21, 27, 227]}
        Impuestos.objects.filter(
            contribuyente=contribuyente
        ).exclude(
            impuesto__in=impuestos[0]['impuestos']
        ).delete()

        return JsonResponse({'result': 'true'})

    def get(self, request, *args, **kwargs):

        contribuyente = self.kwargs.get('rfc')
        impuesto = self.kwargs.get('impuesto')
        
        # Obtener tabla generada
        if impuesto != '0':  
            queryset = Impuestos.objects.filter(
                contribuyente=contribuyente,
                impuesto=impuesto
            ).order_by('id')
        else:
            queryset = None

        if queryset:
            # Serializar queryset
            lista = []
            for row in queryset:
                table = {}
                table['id'] = row.id
                table['periodo'] = row.periodo
                table['ejercicio'] = row.ejercicio
                table['ejercicio_1'] = row.ejercicio_1
                table['ejercicio_2'] = row.ejercicio_2
                table['ejercicio_3'] = row.ejercicio_3
                table['ejercicio_4'] = row.ejercicio_4
                table['ejercicio_5'] = row.ejercicio_5
                lista.append(table)

            data = json.dumps(lista)

        else:  
            if impuesto != '0':  
                instancia_contribuyente = Contribuyentes.objects.get(pk=contribuyente)
                instancia_impuesto = Codigos_Maestros.objects.get(pk=impuesto)

                meses = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC']
                bimestres = ['ENE-FEB','MAR-ABR','MAY-JUN','JUL-AGO','SEP-OCT','NOV-DIC']

                lista_mensual = []
                lista_bimestral = []
                lista_anual = []
                ejercicio = date.today().year

                if instancia_impuesto.valor == 'MENSUAL':
                    # Genera el header de la tabla
                    header = Impuestos(
                        contribuyente=instancia_contribuyente,
                        impuesto=instancia_impuesto,
                        periodo='Mes',
                        ejercicio=ejercicio,
                        ejercicio_1=ejercicio - 1,
                        ejercicio_2=ejercicio - 2,
                        ejercicio_3=ejercicio - 3,
                        ejercicio_4=ejercicio - 4,
                        ejercicio_5=ejercicio - 5
                    )
                    lista_mensual.append(header)

                    # Genera los periodos
                    for item in meses:
                        datos = Impuestos(
                            contribuyente=instancia_contribuyente,
                            impuesto=instancia_impuesto,
                            periodo=item,
                            ejercicio=0,
                            ejercicio_1=0,
                            ejercicio_2=0,
                            ejercicio_3=0,
                            ejercicio_4=0,
                            ejercicio_5=0
                        )
                        lista_mensual.append(datos)

                    Impuestos.objects.bulk_create(lista_mensual)

                elif instancia_impuesto.valor == 'BIMESTRAL':
                    # Genera el header de la tabla
                    header = Impuestos(
                        contribuyente=instancia_contribuyente,
                        impuesto=instancia_impuesto,
                        periodo='Bimestre',
                        ejercicio=ejercicio,
                        ejercicio_1=ejercicio - 1,
                        ejercicio_2=ejercicio - 2,
                        ejercicio_3=ejercicio - 3,
                        ejercicio_4=ejercicio - 4,
                        ejercicio_5=ejercicio - 5
                    )
                    lista_bimestral.append(header)

                    # Genera los periodos
                    for item in bimestres:
                        datos = Impuestos(
                            contribuyente=instancia_contribuyente,
                            impuesto=instancia_impuesto,
                            periodo=item,
                            ejercicio=0,
                            ejercicio_1=0,
                            ejercicio_2=0,
                            ejercicio_3=0,
                            ejercicio_4=0,
                            ejercicio_5=0
                        )
                        lista_bimestral.append(datos)

                    Impuestos.objects.bulk_create(lista_bimestral)

                elif instancia_impuesto.valor == 'ANUAL':
                    # Genera el header de la tabla
                    header = Impuestos(
                        contribuyente=instancia_contribuyente,
                        impuesto=instancia_impuesto,
                        periodo='',
                        ejercicio=ejercicio,
                        ejercicio_1=ejercicio - 1,
                        ejercicio_2=ejercicio - 2,
                        ejercicio_3=ejercicio - 3,
                        ejercicio_4=ejercicio - 4,
                        ejercicio_5=ejercicio - 5
                    )
                    lista_anual.append(header)

                    # Genera el año
                    datos = Impuestos(
                        contribuyente=instancia_contribuyente,
                        impuesto=instancia_impuesto,
                        periodo='ANUAL',
                        ejercicio=0,
                        ejercicio_1=0,
                        ejercicio_2=0,
                        ejercicio_3=0,
                        ejercicio_4=0,
                        ejercicio_5=0
                    )
                    lista_anual.append(datos)

                    Impuestos.objects.bulk_create(lista_anual)

                # Obtener tabla generada
                queryset = Impuestos.objects.filter(
                    contribuyente=contribuyente,
                    impuesto=impuesto
                ).order_by('id')

                # Serializar queryset
                lista = []
                for row in queryset:
                    table = {}
                    table['id'] = row.id
                    table['periodo'] = row.periodo
                    table['ejercicio'] = row.ejercicio
                    table['ejercicio_1'] = row.ejercicio_1
                    table['ejercicio_2'] = row.ejercicio_2
                    table['ejercicio_3'] = row.ejercicio_3
                    table['ejercicio_4'] = row.ejercicio_4
                    table['ejercicio_5'] = row.ejercicio_5
                    lista.append(table)

                data = json.dumps(lista)
            else:
                data = None
            
        return HttpResponse(data, 'application/json')


class Terminar_Contribuyente(LoginRequiredMixin, TemplateView):
    template_name = 'programacion/editar/terminar.html'

    def get_context_data(self, **kwargs):
        context = super(Terminar_Contribuyente, self).get_context_data(**kwargs)

        context['form'] = CerrarAnalisisForm
        
        return context

    def delete(self, request, *args, **kwargs):
        id = self.kwargs['pk']
        
        instance = Contribuyentes.objects.get(id = str(id))
        instance.is_ready = True
        instance.save()

        messages.info(self.request, 'en_proceso')

        return JsonResponse({'result': 'true'})

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']
        
        instance = Contribuyentes.objects.get(id = str(id))

        obj_estatus = Codigos_Maestros.objects.filter(codigo='XXTAKE_TAXPAYERS', id=request.POST.get('estatus'))
        obj_motivo = Codigos_Maestros.objects.filter(codigo='XXREASON', id=request.POST.get('motivo'))

        instance.estatus = obj_estatus[0].comentario
        # instance.monto = request.POST['monto']
        instance.motivo = obj_motivo[0].comentario
        instance.comentarios=request.POST['comentarios']
        instance.fecha_fin = date.today()
        instance.save()

        messages.info(self.request, 'en_proceso')

        return redirect(self.request.META['HTTP_REFERER'])


class Validar_Contribuyente(View):

    def get(self, request, *args, **kwargs):

        username = self.request.user.username
        flag = False
        rfc = self.kwargs.get('rfc')
        opcion = self.kwargs.get('opcion')

        if opcion == 0:
            # Buscar si hay RFC Disponibles
            auditoria_rfcs = Programa_Transferidos.objects.filter(
                ~Q(usuario=''),
                area = 'AUDITORIA',
                is_active = True,
                estatus__in = ['ACEPTADO','ACTIVO','CIERRE']
            ).values('rfc')

            vigilancia_rfcs = Programa.objects.all().exclude(
                estatus__in = ['CONCLUIDO']
            ).values('rfc')

            queryset = Contribuyentes.objects.filter(
                usuario = None
            ).order_by(
                'prioridad'
            ).exclude(
                rfc__in = auditoria_rfcs
            ).exclude(
                rfc__in = vigilancia_rfcs
            ).first()

            if queryset:
                flag = True

        elif opcion == 1:
            if Contribuyentes.objects.filter(rfc=rfc, usuario=username,estatus='PROCEDENTE',is_ready=False).exists():
                flag = True

        else:
            if Contribuyentes.objects.filter(rfc=rfc,usuario=None).exists():
                flag = True

        return JsonResponse({'result': flag})


class Carga_Archivos_Contribuyente(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_archivos')
    
    model = Archivos_Contribuyente
    template_name = 'programacion/crear/archivos_contribuyente.html'
    form_class = Archivos_Contribuyente_Form
    
    def get_context_data(self, **kwargs):
        context = super(Carga_Archivos_Contribuyente, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        
        return context

    def get_form_kwargs(self):
        kwargs = super(Carga_Archivos_Contribuyente, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def form_valid(self, form):           
        form.instance.usuario = self.request.user.username

        return super(Carga_Archivos_Contribuyente, self).form_valid(form)

    def get_success_url(self):
        messages.info(self.request, 'archivos')
        messages.success(self.request, 'Archivo cargado exitosamente!')

        user = self.request.user.username

        redirect = User.objects.filter(username=user, groups__name__in=['COORDINACION PROGRAMACION','COORDINACION VIGILANCIA', 'EJECUTIVO ANALISIS']).exists()

        if redirect:
            return reverse_lazy('programacion_app:autorizacion')
        else:
            return reverse_lazy('programacion_app:admin-programacion', kwargs={'id': self.object.programa_id })


class Get_Files_Programacion(View):

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get('pk')
        user = self.request.user.username

        data = []
        lista = []
        for row in Archivos_Contribuyente.objects.filter(contribuyente=pk):
            data_file = {}
            data_file['id'] = row.id
            data_file['tipo'] = row.tipo 
            if row.comentarios:
                data_file['comentarios'] = row.comentarios
            else:
                data_file['comentarios'] = ''
            data_file['url'] = row.archivo.url
            data_file['nombre'] = row.archivo.name[19:]
            data_file['size'] = row.archivo.size
            if user == row.usuario:
                data_file['editar'] = ''
            else:
                data_file['editar'] = 'disabled'

            lista.append(data_file)

        data = json.dumps(lista)

        return HttpResponse(data, 'application/json')


class Get_Files_Vigilancia(View):

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get('pk')
        user = self.request.user.username

        data = []
        lista = []
        for row in Archivos.objects.filter(programa_id=pk).order_by('-id'):
            data_file = {}
            data_file['id'] = row.id
            data_file['tipo'] = row.tipo 
            if row.comentarios:
                data_file['comentarios'] = row.comentarios
            else:
                data_file['comentarios'] = ''
            data_file['url'] = row.archivo.url
            data_file['nombre'] = row.archivo.name[19:]
            data_file['size'] = row.archivo.size
            if user == row.usuario:
                data_file['editar'] = ''
            else:
                data_file['editar'] = 'disabled'

            lista.append(data_file)

        data = json.dumps(lista)

        return HttpResponse(data, 'application/json')


class Subir_Archivos_Programacion(TemplateView):
    template_name = 'programacion/crear/subir_archivos_programacion.html'

    def get_context_data(self, **kwargs):
        context = super(Subir_Archivos_Programacion, self).get_context_data(**kwargs)

        context['pk'] = self.kwargs.get('pk')
        context['tipo'] = Codigos_Maestros.objects.filter(codigo='XXFILE')

        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        instancia_contribuyente = Contribuyentes.objects.get(pk=pk)

        archivo = request.FILES['file']

        Archivos_Contribuyente(
            contribuyente=instancia_contribuyente,
            archivo=archivo,
            fecha=date.today(),
            usuario=self.request.user.username
        ).save()

        return JsonResponse({'res': 'ok'})


class Subir_Archivos_Vigilancia(TemplateView):
    template_name = 'programacion/crear/subir_archivos_vigilancia.html'

    def get_context_data(self, **kwargs):
        context = super(Subir_Archivos_Vigilancia, self).get_context_data(**kwargs)

        context['pk'] = self.kwargs.get('pk')
        context['tipo'] = Codigos_Maestros.objects.filter(codigo='XXFILE')

        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        instancia_contribuyente = Programa.objects.get(pk=pk)

        archivo = request.FILES['file']

        Archivos(
            programa_id=instancia_contribuyente,
            archivo=archivo,
            fecha=date.today(),
            usuario=self.request.user.username
        ).save()

        return JsonResponse({'res': 'ok'})


class Eliminar_Archivo_Programacion(View):

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        
        instancia_archivo = Archivos_Contribuyente.objects.get(pk=pk)
        instancia_archivo.delete()

        return JsonResponse({'res': 'ok'})


class Eliminar_Archivo_Vigilancia(View):

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        
        instancia_archivo = Archivos.objects.get(pk=pk)
        instancia_archivo.delete()

        return JsonResponse({'res': 'ok'})


class Guardar_Archivos_Programacion(View):

    def post(self, request, *args, **kwargs):

        # Convertir data a Diccionario de python
        formData = ast.literal_eval(request.POST['data'])

        with transaction.atomic():
            for value in formData:
                Archivos_Contribuyente.objects.filter(
                    pk=value['id']
                ).update(
                    tipo = value['tipo'],
                    comentarios = value['comentarios']
                )

        return JsonResponse({'result': 'true'})


class Guardar_Archivos_Vigilancia(View):

    def post(self, request, *args, **kwargs):

        # Convertir data a Diccionario de python
        formData = ast.literal_eval(request.POST['data'])

        with transaction.atomic():
            for value in formData:
                Archivos.objects.filter(
                    pk=value['id']
                ).update(
                    tipo = value['tipo'],
                    comentarios = value['comentarios']
                )

        return JsonResponse({'result': 'true'})
