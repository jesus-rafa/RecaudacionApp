import datetime
import csv
import os
import json
import ast
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.base import View
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView
)
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import DeleteView, FormView
from django.db.models import Q, OuterRef, Subquery, Count, Sum, CharField, Value, F, DurationField, ExpressionWrapper
from django.db.models.functions import Concat, ExtractDay
from django.contrib.postgres.aggregates.general import ArrayAgg
from applications.rec.models import Contacto, REC, Busquedas, Fiscalizados, Cartas_Invitacion
from applications.home.models import Codigos_Maestros
from applications.users.models import User
from applications.programacion.models import Programa, Detalle
from applications.padrones.models import Programa_Padrones
from django.conf import settings
from django.db import transaction

from .models import Programa_Transferidos, Detalle_Transferidos, Pagos_Transferidos, Archivos_Transferidos, Temporal, Impuestos
from .forms import (
    RechazarForm, 
    AceptarForm, 
    TransferenciaForm, 
    OpcionForm, 
    ContribuyenteForm, 
    ArchivosForm, 
    DetalleForm, 
    PagosForm, 
    RechazarTodosForm, 
    AceptarTodosForm,
    AsignarAuditoriaForm,
    ContribuyenteEjecucionForm,
    BatchForm,
    FechaCierreForm,
    ImpuestosForm
)
from django.db import connection
from applications.users.mixins import GlobalMixin, CRUDMixin


# ============================= ListView ================================================ #
class Lista_Transferencias(GlobalMixin, ListView):
    template_name = 'transferidos/lista_transferencias.html'
    model = Programa_Transferidos
    context_object_name = 'propuestas'

    def get_queryset(self):

        estatus = Detalle.objects.filter(
            programa_id=OuterRef('pk'),
            estatus__in=['NO LOCALIZADO','NEGACION DE AUTOCORRECION'],
            is_active=True
        ).order_by('-fecha')

        transferir_ejecucion = Detalle.objects.filter(
            programa_id=OuterRef('pk'),
            estatus__in=['PARA TRANSFERIR'],
            comentarios__icontains = '[Se propone transferencia a EJECUCIÓN]',
            is_active=True
        ).order_by('-fecha')

        autorizacion = Detalle.objects.filter(
            programa_id=OuterRef('pk'),
            estatus='OFICIO'
        ).order_by('-fecha')

        queryset = Programa.objects.filter(
            estatus='PROPUESTA TRANSFERENCIA'
        ).annotate(
            estatus_cierre=Subquery(estatus.values('estatus')[:1]),
            transferir_ejecucion=Subquery(transferir_ejecucion.values('comentarios')[:1]),
            fecha_autorizacion=Subquery(autorizacion.values('fecha')[:1])
        )

        # queryset = Programa_Transferidos.objects.filter(
        #     ~Q(nuevo_folio=''),
        #     is_active=False,
        #     estatus='TRANSFERIDO'
        # ).values(
        #     'nuevo_folio', 'area', 'fecha'
        # ).annotate(
        #     sum_rfc=Count('rfc'),
        #     sum_presuntiva=Sum('presuntiva')
        # ).order_by()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(Lista_Transferencias, self).get_context_data(**kwargs)

        context['transferencias'] = Programa_Transferidos.objects.filter(
            # area = 'AUDITORIA',
            is_active=True,
            estatus='TRANSFERIDO'
           
        )

        context['aceptadas'] = Programa_Transferidos.objects.filter(
            #~Q(nuevo_folio=''),
            # area='AUDITORIA',
            is_active=True,
            estatus__in= ['ACEPTADO','CONCLUIDO' ],
            usuario='gcisnerosg'
        )

        context['rechazadas'] = Programa_Transferidos.objects.filter(
            # area='AUDITORIA',
            is_active=True,
            estatus='RECHAZADO'
        )


        # queryset = Programa_Transferidos.objects.filter(
        #     ~Q(nuevo_folio=''),
        #     is_active=True,
        #     etapa__in=['CIERRE','TRANSFERIDO','NUEVO','SEGUIMIENTO']
        # ).values(
        #     'nuevo_folio', 'area'
        # ).annotate(
        #     sum_rfc=Count('rfc'),
        #     sum_presuntiva=Sum('presuntiva'),
        #     sum_transferidos=Sum(
        #         Case(
        #             When(estatus='TRANSFERIDO', then=1), default=0, output_field=IntegerField()
        #         )
        #     ),
        #     sum_rechazados=Sum(
        #         Case(
        #             When(estatus='RECHAZADO', then=1), default=0, output_field=IntegerField()
        #         )
        #     ),
        #     sum_nuevos=Sum(
        #         Case(
        #             When(estatus='NUEVO', then=1), default=0, output_field=IntegerField()
        #         )
        #     )
        # ).order_by()
        # context['enviados'] = queryset

        return context


class Admin_Areas(LoginRequiredMixin, ListView):
    template_name = 'transferidos/admin_areas.html'
    context_object_name = 'transferidos'

    def get_queryset(self):
        start = self.kwargs.get('folio')[:-5]
        end = self.kwargs.get('folio')[-5:].replace('-', '/')
        nuevo_folio = self.kwargs.get('folio')

        if Programa_Transferidos.objects.filter(nuevo_folio=nuevo_folio, is_active=True).exists():
            queryset = Programa_Transferidos.objects.filter(
                nuevo_folio=nuevo_folio,
                is_active=True,
                estatus='TRANSFERIDO'
            )
        else:
            queryset = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super(Admin_Areas, self).get_context_data(**kwargs)

        start = self.kwargs.get('folio')[:-5]
        end = self.kwargs.get('folio')[-5:].replace('-', '/')
        nuevo_folio = self.kwargs.get('folio')

        context['folio'] = nuevo_folio

        if Programa_Transferidos.objects.filter(
                nuevo_folio=nuevo_folio, is_active=True).exists():
            obj = Programa_Transferidos.objects.filter(
                nuevo_folio=nuevo_folio, is_active=True)[:1]
            area = str(obj[0].area)
        else:
            area = 'Sin contribuyentes'

        context['area'] = area

        return context


class Admin_Transferencias(LoginRequiredMixin, ListView):
    template_name = 'transferidos/admin_transferencias.html'
    context_object_name = 'transferidos'

    def get_queryset(self):
        nuevo_folio = self.kwargs.get('folio')

        if Programa_Transferidos.objects.filter(nuevo_folio=nuevo_folio).exists():
            queryset = Programa_Transferidos.objects.filter(
                nuevo_folio=nuevo_folio)
        else:
            queryset = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super(Admin_Transferencias, self).get_context_data(**kwargs)

        nuevo_folio = self.kwargs.get('folio')

        context['folio'] = nuevo_folio

        if Programa_Transferidos.objects.filter(
                nuevo_folio=nuevo_folio).exists():
            obj = Programa_Transferidos.objects.filter(
                nuevo_folio=nuevo_folio)
            area = str(obj[0].area)
        else:
            area = 'Sin contribuyentes'

        context['area'] = area

        return context


class Aceptar(LoginRequiredMixin, FormView):
    template_name = "transferidos/aceptar.html"
    form_class = AceptarForm
    success_message = "aceptado correctamente!"

    def form_valid(self, form):

        id = form.cleaned_data['folio']

        obj = Programa_Transferidos.objects.get(id=id)
        obj.estatus = 'ACEPTADO'
        obj.save()

        Detalle_Transferidos.objects.create(
            programa_id=obj,
            fecha=datetime.date.today(),
            comentarios='',
            estatus='ACEPTADO',
            usuario=self.request.user.username
        )

        # query = Programa_Transferidos.objects.filter(
        #     nuevo_folio=folio,
        #     is_active=False
        # )

        # for row in query:
        #     obj = Programa.objects.get(folio=row.folio)
        #     obj.estatus = 'CONCLUIDO'
        #     obj.save()

        #     Detalle.objects.create(
        #         programa_id=obj,
        #         fecha=datetime.date.today(),
        #         comentarios='',
        #         estatus='CONCLUIDO',
        #         usuario=self.request.user.username
        #     )

        # Programa_Transferidos.objects.filter(
        #     nuevo_folio=folio
        # ).update(
        #     is_active=True,
        #     fecha=datetime.date.today()
        # )

        return super(Aceptar, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('transferidos_app:lista-transferencias')


class Opcion(LoginRequiredMixin, FormView):
    template_name = "transferidos/opcion.html"
    form_class = OpcionForm
    success_message = "Guardado correctamente!"

    # def get_context_data(self, **kwargs):
    #     context = super(Opcion, self).get_context_data(**kwargs)

    #     context['no_control'] = self.kwargs.get('no_control')
    #     return context

    def form_valid(self, form):

        id = form.cleaned_data['lista']

        if form.cleaned_data['comentarios']:
            cmmt = form.cleaned_data['comentarios']
        else:
            cmmt = ''

        if form.cleaned_data['opcion'] == 'ACEPTAR':
            obj = Programa_Transferidos.objects.get(id=id)
            obj.estatus = 'ACEPTADO'
            obj.metodo_envio = str(form.cleaned_data['metodo_envio'])
            obj.save()

            Detalle_Transferidos.objects.create(
                programa_id=obj,
                fecha=datetime.date.today(),
                comentarios=cmmt,
                estatus='ACEPTADO',
                usuario=self.request.user.username
            )
        else:
            obj = Programa_Transferidos.objects.get(id=id)
            obj.estatus = 'RECHAZADO'
            obj.save()
            
            Detalle_Transferidos.objects.create(
                programa_id=obj,
                fecha=datetime.date.today(),
                comentarios=cmmt,
                estatus='RECHAZADO',
                usuario=self.request.user.username
            )

        return super(Opcion, self).form_valid(form)

    def get_success_url(self):
        if self.request.user.area == 'AUDITORIA':
            return reverse_lazy('transferidos_app:lista-auditoria')
        else:
            return reverse_lazy('transferidos_app:lista-ejecucion')


class Rechazar(LoginRequiredMixin, FormView):

    template_name = "transferidos/rechazar.html"
    form_class = RechazarForm
    success_message = "Rechazado correctamente!"

    def get_context_data(self, **kwargs):
        context = super(Rechazar, self).get_context_data(**kwargs)

        folio = self.kwargs.get('folio')
        # obj = Programa_Transferidos.objects.filter(id=id)
        # folio = obj[0].nuevo_folio
        # start = folio[:-5]
        # end = folio[-5:].replace('-', '/')
        # new_folio = start + end

        # print(new_folio)

        context['new_folio'] = folio
        return context

    def form_valid(self, form):

        id = form.cleaned_data['lista']

        instance = Programa_Transferidos.objects.get(id=id)
        instance.delete()

        old_folio = form.cleaned_data['old_folio']
        comentarios = form.cleaned_data['comentarios']

        obj = Programa.objects.get(folio=old_folio)
        obj.etapa = 'CIERRE'
        obj.estatus = 'RECHAZADO'
        obj.save()

        Detalle.objects.create(
            programa_id=obj,
            fecha=datetime.date.today(),
            comentarios=comentarios,
            estatus='RECHAZADO',
            usuario=self.request.user.username
        )

        start = self.kwargs.get('folio')[:-5]
        end = self.kwargs.get('folio')[-5:].replace('-', '/')
        nuevo_folio = start + end

        num_folios = Programa_Transferidos.objects.filter(
            nuevo_folio=nuevo_folio
        ).count()

        # if num_folios == 0:
            # obj = Oficios.objects.get(folio=nuevo_folio)
            # obj.estatus = 'CANCELADO'
            # obj.save()

        return super(Rechazar, self).form_valid(form)

    def get_success_url(self):
        folio = self.kwargs.get('folio')
        # start = folio[:-5]
        # end = folio[-5:].replace('-', '/')
        # new_folio = start + end

        return reverse_lazy('transferidos_app:admin-transferencias', kwargs={'folio': folio})

    # def post(self, request, *args, **kwargs):

    #     id = request.POST.get('lista', None)
    #     old_folio = request.POST.get('old_folio', None)
    #     comentarios = request.POST.get('comentarios', None)

    #     data = {
    #         'obj': old_folio
    #     }

    #     message = old_folio
    #     error = 'No hay error!'
    #     response = JsonResponse({'message': message, 'error': error})
    #     return response


class Lista_Auditoria(GlobalMixin, ListView):
    template_name = 'transferidos/lista_auditoria.html'
    model = Programa_Transferidos
    context_object_name = 'transferidos'

    def get_queryset(self):

        estatus = Detalle_Transferidos.objects.filter(
            programa_id=OuterRef('pk'),
            estatus = 'TRANSFERIDO',
            is_active=True
        ).order_by('-fecha')

        queryset = Programa_Transferidos.objects.filter(
            area = 'AUDITORIA',
            estatus__in=['TRANSFERIDO'],
            is_active=True
        ).annotate(
            comentarios_recaudacion=Subquery(estatus.values('comentarios')[:1])
        )

        # queryset = Programa_Transferidos.objects.filter(
        #     area='AUDITORIA',
        #     is_active=True,
        #     estatus='TRANSFERIDO'
        # ).values(
        #     'nuevo_folio', 'area', 'fecha'
        # ).annotate(
        #     sum_rfc=Count('rfc'),
        #     sum_presuntiva=Sum('presuntiva')
        # ).order_by()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Lista_Auditoria, self).get_context_data(**kwargs)

        # context['nuevos'] = Programa_Transferidos.objects.filter(
        #     area='AUDITORIA',
        #     is_active=True,
        #     etapa='NUEVO',
        #     estatus='NUEVO'
        # )

        context['rechazados'] = Programa_Transferidos.objects.filter(
            area='AUDITORIA',
            is_active=True,
            estatus='RECHAZADO'
        )

        return context
        

class Activos_Ejecucion(GlobalMixin, ListView):
    template_name = 'transferidos/activos_ejecucion.html'
    model = Programa_Transferidos
    context_object_name = 'programacion'

    def get_queryset(self):
        queryset = Programa_Transferidos.objects.filter(
            ~Q(usuario=''),
            area = 'EJECUCION',
            is_active = True,
            estatus__in = ['ACEPTADO', 'ACTIVO']
        )

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(Activos_Ejecucion, self).get_context_data(**kwargs)

        context['hoy'] = datetime.date.today()

        return context


class Activos_Auditoria(GlobalMixin, ListView):
    template_name = 'transferidos/activos_auditoria.html'
    model = Programa_Transferidos
    context_object_name = 'programacion'

    def get_queryset(self):

        estatus = Detalle_Transferidos.objects.filter(
            programa_id=OuterRef('pk'),
            estatus = 'CIERRE'
        ).order_by('-fecha')

        queryset = Programa_Transferidos.objects.filter(
            area = 'AUDITORIA',
            is_active = True,
            estatus__in = ['ACEPTADO', 'ACTIVO','CIERRE']
        ).annotate(
            estatus_cierre=Subquery(estatus.values('fecha')[:1])
        )

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(Activos_Auditoria, self).get_context_data(**kwargs)

        context['hoy'] = datetime.date.today()

        return context


class Lista_Programacion_Auditoria(GlobalMixin, ListView):
    template_name = 'transferidos/lista_programacion_auditoria.html'
    model = Programa_Transferidos
    context_object_name = 'programacion'

    def get_queryset(self):
        queryset = Programa_Transferidos.objects.filter(
            area = 'AUDITORIA',
            is_active = True,
            estatus__in = ['ACEPTADO', 'ACTIVO']
        )

        return queryset
        #return Programa_Transferidos.objects.filter(area='AUDITORIA').exclude(estatus__in=['NUEVO', 'CANCELADA', 'PROPUESTA', 'PRESUNTIVA', 'FAFD', '1-RECHAZADA', '2-RECHAZADA', '3-RECHAZADA', 'OFICIO', 'CONCLUIDO', 'TRANSFERIDO', 'RECHAZADO'])

    def get_context_data(self, **kwargs):
        context = super(Lista_Programacion_Auditoria, self).get_context_data(**kwargs)

        context['concluidos'] = Programa_Transferidos.objects.filter(area='AUDITORIA', estatus='CONCLUIDO')

        return context


class Concluidos_Ejecucion(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'transferidos/ejecucion/concluidos.html'
    model = Programa_Transferidos
    context_object_name = 'programacion'

    def get_context_data(self, **kwargs):
        context = super(Concluidos_Ejecucion, self).get_context_data(**kwargs)

        context['total_concluidos'] = Programa_Transferidos.objects.filter(
            ~Q(usuario=''),
            area = 'EJECUCION',
            is_active = True,
            estatus = 'CONCLUIDO'
        ).count()

        context['metodo_envio'] = Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD_EJECUCION').order_by('-id')

        return context

    def get_queryset(self):

        kword=self.request.GET.get("kword", '')
        metodo_envio=self.request.GET.get("metodo_envio", '')

        if kword != '' or metodo_envio != '':

            queryset = Programa_Transferidos.objects.filtrar(
                kword=kword,
                metodo_envio=metodo_envio,
                estatus='CONCLUIDO',
            )

            # queryset = Programa_Transferidos.objects.filter(
            #     ~Q(usuario=''),
            #     Q(rfc__icontains = kword) | Q(nombre__icontains = kword),
            #     area = 'EJECUCION',
            #     is_active = True,
            #     estatus = 'CONCLUIDO'
            # ).order_by('rfc')

            self.paginate_by = queryset.count()

        else:
            queryset = Programa_Transferidos.objects.filter(
                ~Q(usuario=''),
                area = 'EJECUCION',
                is_active = True,
                estatus = 'CONCLUIDO'
            ).order_by('-id')
        return queryset


class Seguimiento_Ejecucion(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'transferidos/ejecucion/seguimiento.html'
    model = Programa_Transferidos
    context_object_name = 'programacion'

    def get_context_data(self, **kwargs):
        context = super(Seguimiento_Ejecucion, self).get_context_data(**kwargs)

        context['total_seguimiento'] = Programa_Transferidos.objects.filter(
            ~Q(usuario=''),
            area = 'EJECUCION',
            is_active = True,
            estatus = 'ACTIVO'
        ).count()

        context['metodo_envio'] = Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD_EJECUCION').order_by('-id')

        return context

    def get_queryset(self):

        kword=self.request.GET.get("kword", '')
        metodo_envio=self.request.GET.get("metodo_envio", '')

        if kword != '' or metodo_envio != '':

            queryset = Programa_Transferidos.objects.filtrar(
                kword=kword,
                metodo_envio=metodo_envio,
                estatus='ACTIVO',
            )
            
            # queryset = Programa_Transferidos.objects.filter(
            #     Q(rfc__icontains = kword) | Q(nombre__icontains = kword)
            # ).filter(
            #     metodo_envio=metodo_envio
            # ).filter(
            #     ~Q(usuario=''),
            #     area = 'EJECUCION',
            #     is_active = True,
            #     estatus = 'ACTIVO'
            # ).order_by('rfc')

            self.paginate_by = queryset.count()

        else:

            queryset = Programa_Transferidos.objects.filter(
                ~Q(usuario=''),
                area = 'EJECUCION',
                is_active = True,
                estatus = 'ACTIVO'
            ).order_by('-id')

        return queryset
   
        
class Seguimiento_Auditoria(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'transferidos/auditoria/seguimiento.html'
    model = Programa_Transferidos
    context_object_name = 'programacion'

    def get_context_data(self, **kwargs):
        context = super(Seguimiento_Auditoria, self).get_context_data(**kwargs)

        context['total_seguimiento'] = Programa_Transferidos.objects.filter(
            ~Q(usuario=''),
            area = 'AUDITORIA',
            is_active = True,
            estatus__in = ['ACEPTADO','ACTIVO','CIERRE']
        ).count()

        context['metodo_envio'] = Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD').order_by('-id')

        return context

    def get_queryset(self):

        kword=self.request.GET.get("kword", '')
        metodo_envio=self.request.GET.get("metodo_envio", '')

        impuestos = Impuestos.objects.values(
            'contribuyente'
        ).annotate(
            impuestos=ArrayAgg(
                Concat(
                    'impuesto__comentario',
                    Value('_'),
                    'impuesto__id',
                    output_field=CharField()
                ), distinct=True)
        ).filter(
            Q(ejercicio = 1) | Q(ejercicio_1 = 1) | Q(ejercicio_2 = 1) | Q(ejercicio_3 = 1) | Q(ejercicio_4 = 1) | Q(ejercicio_5 = 1),
            contribuyente=OuterRef('pk')
        ).order_by()

        if kword != '' or metodo_envio != '':
            lista_estatus = ['ACEPTADO','ACTIVO','CIERRE']

            queryset = Programa_Transferidos.objects.filtrar_auditoria(
                list=lista_estatus,
                kword=kword,
                metodo_envio=metodo_envio,
            ).annotate(
                impuestos=Subquery(impuestos.values('impuestos')[:1])
            )

            self.paginate_by = queryset.count()

        else:
            queryset = Programa_Transferidos.objects.filter(
                ~Q(usuario=''),
                area = 'AUDITORIA',
                is_active = True,
                estatus__in = ['ACEPTADO','ACTIVO','CIERRE']
            ).annotate(
                impuestos=Subquery(impuestos.values('impuestos')[:1])
            ).order_by('-id')

        return queryset


class Concluidos_Auditoria(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'transferidos/auditoria/concluidos.html'
    model = Programa_Transferidos
    context_object_name = 'concluidos'

    def get_context_data(self, **kwargs):
        context = super(Concluidos_Auditoria, self).get_context_data(**kwargs)

        context['total_concluidos'] = Programa_Transferidos.objects.filter(
            ~Q(usuario=''),
            area = 'AUDITORIA',
            is_active = True,
            estatus = 'CONCLUIDO'
        ).count()

        context['metodo_envio'] = Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD').order_by('-id')

        return context

    def get_queryset(self):

        kword=self.request.GET.get("kword", '')
        metodo_envio=self.request.GET.get("metodo_envio", '')

        impuestos = Impuestos.objects.values(
            'contribuyente'
        ).annotate(
            impuestos=ArrayAgg(
                Concat(
                    'impuesto__comentario',
                    Value('_'),
                    'impuesto__id',
                    output_field=CharField()
                ), distinct=True)
        ).filter(
            Q(ejercicio = 1) | Q(ejercicio_1 = 1) | Q(ejercicio_2 = 1) | Q(ejercicio_3 = 1) | Q(ejercicio_4 = 1) | Q(ejercicio_5 = 1),
            contribuyente=OuterRef('pk')
        ).order_by()

        if kword != '' or metodo_envio != '':
            lista_estatus = ['CONCLUIDO']
            
            queryset = Programa_Transferidos.objects.filtrar_auditoria(
                list=lista_estatus,
                kword=kword,
                metodo_envio=metodo_envio,
            ).annotate(
                impuestos=Subquery(impuestos.values('impuestos')[:1])
            )

            self.paginate_by = queryset.count()

        else:

            queryset = Programa_Transferidos.objects.filter(
                ~Q(usuario=''),
                area='AUDITORIA', 
                is_active = True,
                estatus='CONCLUIDO'
            ).annotate(
                impuestos=Subquery(impuestos.values('impuestos')[:1])
            ).order_by('-id')

        return queryset


class Lista_Programacion_Ejecucion(LoginRequiredMixin, ListView):
    template_name = 'transferidos/lista_programacion_ejecucion.html'
    model = Programa_Transferidos
    context_object_name = 'programacion'

    def get_queryset(self):
        #return Programa_Transferidos.objects.filter(area='EJECUCION').exclude(estatus__in=['NUEVO', 'CANCELADA', 'PROPUESTA', 'PRESUNTIVA', 'FAFD', '1-RECHAZADA', '2-RECHAZADA', '3-RECHAZADA', 'OFICIO', 'CONCLUIDO', 'TRANSFERIDO', 'RECHAZADO'])
        return Programa_Transferidos.objects.filter(
            ~Q(usuario=''),
            #~Q(estatus='CONCLUIDO'),
            #~Q(estatus='RECHAZADO'),
            estatus='ACTIVO',
            area='EJECUCION',
            is_active=True
        )

    def get_context_data(self, **kwargs):
        context = super(Lista_Programacion_Ejecucion, self).get_context_data(**kwargs)

        context['concluidos'] = None

        return context


class Solicitudes_Apoyo(GlobalMixin, ListView):
    template_name = 'transferidos/solicitudes_apoyo.html'
    model = Programa_Transferidos
    context_object_name = 'programacion'

    def get_queryset(self):
        queryset = Programa.objects.filter(
            ~Q(estatus='RECHAZADO'),
            ~Q(detalle_programa__estatus='SOLICITUD CONCLUIDA'),
            detalle_programa__estatus='SOLICITUD ACEPTADA'
        )

        return queryset        

    def get_context_data(self, **kwargs):
        context = super(Solicitudes_Apoyo, self).get_context_data(**kwargs)

        context['concluidos'] = Programa.objects.filter(
            detalle_programa__estatus='SOLICITUD CONCLUIDA'
        )

        return context


class Lista_Ejecucion(GlobalMixin, ListView):
    template_name = 'transferidos/lista_ejecucion.html'
    model = Programa_Transferidos
    context_object_name = 'transferidos'

    def get_queryset(self):

        # queryset = Programa_Transferidos.objects.filter(
        #     area='EJECUCION',
        #     is_active=True,
        #     estatus='TRANSFERIDO'
        # ).values(
        #     'nuevo_folio', 'area', 'fecha'
        # ).annotate(
        #     sum_rfc=Count('rfc'),
        #     sum_presuntiva=Sum('presuntiva')
        # ).order_by()

        queryset = Programa_Transferidos.objects.filter(
            estatus='NUEVO',
            area='EJECUCION',
            is_active=True
        )

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(Lista_Ejecucion, self).get_context_data(**kwargs)

        context['activos'] = Programa_Transferidos.objects.filter(
            area='EJECUCION',
            is_active=True,
            seguimiento='',
            estatus__in=['ACEPTADO','ACTIVO']
        )

        context['rechazados'] = Programa_Transferidos.objects.filter(
            area='EJECUCION',
            is_active=True,
            estatus='RECHAZADO'
        )
        
        context['solicitud_apoyo'] = Programa.objects.filter(
            detalle_programa__estatus='SOLICITUD'
            #seguimiento__icontains=user
        ).exclude(
            estatus__in=['CONCLUIDO', 'SOLICITUD ACEPTADA', 'RECHAZADO']
        ).distinct('id')

        return context



class Alta_Transferencia(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'transferidos/alta_transferencia.html'
    form_class = TransferenciaForm
    success_message = 'Transferencia Exitosa!'

    def form_valid(self, form):
        dependencia = form.cleaned_data['dependencia']
        list_ids = form.cleaned_data['lista'].split(',')

        if str(dependencia) == 'AUDITORIA':

            for id in list_ids:
                if Programa.objects.filter(estatus='PROPUESTA TRANSFERENCIA', pk=id).exists():
                    obj = Programa.objects.get(pk=id)
                    obj.etapa = 'CIERRE'
                    obj.estatus = 'CONCLUIDO'
                    obj.save()

                    Detalle.objects.create(
                        programa_id=obj,
                        fecha=datetime.date.today(),
                        comentarios='',
                        estatus='TRANSFERIDO',
                        usuario=self.request.user.username
                    )

                    Detalle.objects.create(
                        programa_id=obj,
                        fecha=datetime.date.today(),
                        comentarios='',
                        estatus='CONCLUIDO',
                        usuario=self.request.user.username
                    )

                    Programa_Transferidos.objects.create(
                        nuevo_folio='',
                        folio=obj.folio,
                        rfc=obj.rfc,
                        programa=obj.programa,
                        presuntiva=obj.presuntiva,
                        recaudado=obj.recaudado,
                        dias=0,
                        nombre=obj.nombre,
                        direccion=obj.direccion,
                        fecha=datetime.date.today(),
                        etapa='',
                        estatus='TRANSFERIDO',
                        seguimiento='',
                        usuario=self.request.user.username,
                        area=form.cleaned_data['dependencia'],
                        is_active=True
                    )
                    obj_new = Programa_Transferidos.objects.latest('id')

                    Detalle_Transferidos.objects.create(
                        programa_id=obj_new,
                        fecha=datetime.date.today(),
                        comentarios=form.cleaned_data['comentarios'],
                        estatus='TRANSFERIDO',
                        usuario=self.request.user.username
                    )
        else:
            # Transferencia a las dos depemdencias en un movimiento
            for id in list_ids:
                if Programa.objects.filter(estatus='PROPUESTA TRANSFERENCIA', pk=id).exists():
                    obj = Programa.objects.get(pk=id)
                    obj.etapa = 'CIERRE'
                    obj.estatus = 'CONCLUIDO'
                    obj.save()

                    Detalle.objects.create(
                        programa_id=obj,
                        fecha=datetime.date.today(),
                        comentarios='Se Transfiere a AUDITORIA y EJECUCION',
                        estatus='TRANSFERIDO',
                        usuario=self.request.user.username
                    )

                    Detalle.objects.create(
                        programa_id=obj,
                        fecha=datetime.date.today(),
                        comentarios='',
                        estatus='CONCLUIDO',
                        usuario=self.request.user.username
                    )

                    Programa_Transferidos.objects.create(
                        nuevo_folio='',
                        folio=obj.folio,
                        rfc=obj.rfc,
                        programa=obj.programa,
                        presuntiva=obj.presuntiva,
                        recaudado=obj.recaudado,
                        dias=0,
                        nombre=obj.nombre,
                        direccion=obj.direccion,
                        fecha=datetime.date.today(),
                        etapa='',
                        estatus='TRANSFERIDO',
                        seguimiento='',
                        usuario=self.request.user.username,
                        area='AUDITORIA',
                        is_active=True
                    )
                    obj_new_auditoria = Programa_Transferidos.objects.latest('id')

                    Detalle_Transferidos.objects.create(
                        programa_id=obj_new_auditoria,
                        fecha=datetime.date.today(),
                        comentarios=form.cleaned_data['comentarios'],
                        estatus='TRANSFERIDO',
                        usuario=self.request.user.username
                    )

                    Programa_Transferidos.objects.create(
                        nuevo_folio='',
                        folio=obj.folio,
                        rfc=obj.rfc,
                        programa=obj.programa,
                        presuntiva=obj.presuntiva,
                        recaudado=obj.recaudado,
                        dias=0,
                        nombre=obj.nombre,
                        direccion=obj.direccion,
                        fecha=datetime.date.today(),
                        etapa='',
                        estatus='TRANSFERIDO',
                        seguimiento='',
                        usuario=self.request.user.username,
                        area='EJECUCION',
                        is_active=True
                    )

                    obj_new_ejecucion = Programa_Transferidos.objects.latest('id')

                    Detalle_Transferidos.objects.create(
                        programa_id=obj_new_ejecucion,
                        fecha=datetime.date.today(),
                        comentarios=form.cleaned_data['comentarios'],
                        estatus='TRANSFERIDO',
                        usuario=self.request.user.username
                    )
        return super(Alta_Transferencia, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('transferidos_app:lista-transferencias')


class Alta_Ejecucion(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_programa_transferidos')
    
    model = Programa
    template_name = 'transferidos/ejecucion/alta_contribuyente.html'
    form_class = ContribuyenteEjecucionForm
    success_message = 'Contribuyente creado exitosamente!'

    def form_valid(self, form):

        form.instance.rfc = form.cleaned_data['rfc'].upper()
        form.instance.fecha = datetime.date.today()
        form.instance.nuevo_folio = ''
        form.instance.folio = ''
        form.instance.usuario = self.request.user.username
        form.instance.seguimiento = ''
        form.instance.etapa = ''
        form.instance.estatus = 'ACTIVO'
        form.instance.area = self.request.user.area

        form.instance.is_active = True

        return super(Alta_Ejecucion, self).form_valid(form)
        
    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Alta_Contribuyente2(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_programa_transferidos')
    
    model = Programa
    template_name = 'transferidos/auditoria/alta_contribuyente.html'
    form_class = ContribuyenteForm
    success_message = 'Contribuyente creado exitosamente!'

    def form_valid(self, form):

        form.instance.rfc = form.cleaned_data['rfc'].upper()
        form.instance.fecha = datetime.date.today()
        form.instance.nuevo_folio = ''
        form.instance.folio = ''
        form.instance.usuario = self.request.user.username
        form.instance.seguimiento = ''
        form.instance.etapa = ''
        form.instance.programa = ''
        form.instance.estatus = 'ACTIVO'
        form.instance.area = 'AUDITORIA'

        form.instance.is_active = True

        return super(Alta_Contribuyente2, self).form_valid(form)
        
    def get_success_url(self):
    
        # Actualizar RFC Generico al que se genero
        if Programa_Transferidos.objects.filter(rfc=self.request.user.username).exists():
            rfc_generico = Programa_Transferidos.objects.filter(rfc=self.request.user.username).first()
        
            Impuestos.objects.filter(
                contribuyente = rfc_generico
            ).update(
                contribuyente = self.object.id
            )
            # Eliminar RFC Generico
            Programa_Transferidos.objects.filter(rfc=self.request.user.username).delete()

        return self.request.META['HTTP_REFERER']
        

class Editar_Ejecucion(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_programa_transferidos')
    
    model = Programa_Transferidos
    template_name = 'transferidos/ejecucion/editar_contribuyente.html'
    form_class = ContribuyenteEjecucionForm
    success_message = 'Actualizado exitosamente!'

    def form_valid(self, form):
        form.instance.area = self.request.user.area

        return super(Editar_Ejecucion, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(Editar_Ejecucion, self).get_context_data(**kwargs)

        obj = self.get_object()
        selected_program = Codigos_Maestros.objects.filter(comentario=obj.programa)
        context['selected_program'] = selected_program[0].id

        try:
            selected_method = Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD_EJECUCION', comentario=obj.metodo_envio)
            context['selected_method'] = selected_method[0].id
        except:
            context['selected_method'] = None
            
        return context  


    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Editar_Contribuyente(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_programa_transferidos')
    
    model = Programa_Transferidos
    template_name = 'transferidos/auditoria/editar_contribuyente.html'
    form_class = ContribuyenteForm
    success_message = 'Actualizado exitosamente!'

    def form_valid(self, form):
        # Ya no guardara el programa, ahora se usa Impuestos para AUDITORIA
        form.instance.programa = ''
        form.instance.area = 'AUDITORIA'

        return super(Editar_Contribuyente, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(Editar_Contribuyente, self).get_context_data(**kwargs)

        obj = self.get_object()
        # Ya no guardara el programa, ahora se usa Impuestos
        # selected_program = Codigos_Maestros.objects.filter(comentario=obj.programa)
        # context['selected_program'] = selected_program[0].id

        try:
            selected_method = Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD', comentario=obj.metodo_envio)
            context['selected_method'] = selected_method[0].id
        except:
            context['selected_method'] = None

        # Obtener la lista de impuestos guardados
        impuestos = Impuestos.objects.values(
            'impuesto'
        ).filter(
            contribuyente = obj.id
        ).distinct()

        lista_impuestos = Codigos_Maestros.objects.filter(
            codigo = 'XXTAX',
            id__in = impuestos
        ).order_by('id')

        value = []
        for row in lista_impuestos:
            value.append(str(row.comentario) + '_' + str(row.id))
        context['lista_impuestos'] = json.dumps(list(value))
            
        return context  


    def get_success_url(self):
        return self.request.META['HTTP_REFERER']
            
        
class Get_Contribuyente2(ListView):

    model = REC
    template_name = 'transferidos/auditoria/ver_contribuyente.html'

    def get_queryset(self):

        QuerySet = REC.objects.filter(
            rfc__icontains=self.kwargs.get('rfc')
        ).values('nombre', 'direccion')

        return QuerySet

    def get_program_vigilancia(self):

        message = False
        if Programa.objects.filter(~Q(estatus__in=['CONCLUIDO', 'CANCELADA']), rfc__icontains=self.kwargs.get('rfc')).values('programa').exists():
            message = True

        return message

    def get_program_padrones(self):

        message = False
        if Programa_Padrones.objects.filter(~Q(estatus='CONCLUIDO'), rfc__icontains=self.kwargs.get('rfc')).values('programa').exists():
            message = True

        return message
        
    def get_program_auditoria(self):

        message = False
        if Programa_Transferidos.objects.filter(~Q(estatus='CONCLUIDO'), rfc__icontains=self.kwargs.get('rfc'), area='AUDITORIA').values('programa').exists():
            message = True

        return message
        
    def get_program_ejecucion(self):

        message = False
        if Programa_Transferidos.objects.filter(~Q(estatus='CONCLUIDO'), rfc__icontains=self.kwargs.get('rfc'), area='EJECUCION').values('programa').exists():
            message = True

        return message
        
    # def get_program_transferencias(self):
    
        # message = False
        # if Programa_Transferidos.objects.filter(rfc__icontains=kword, estatus="TRANSFERIDO").exists();
            # message = True

        # return message

    def get(self, request, *args, **kwargs):

        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #data = serialize('json', self.get_queryset())

            data = list(self.get_queryset())

            if self.get_program_padrones() or self.get_program_vigilancia() or self.get_program_auditoria() or self.get_program_ejecucion():
                data.append({'message': True})
            else:
                data.append({'message': False})

            # data.append(vigilancia)
            # data.append(padrones)

            # return HttpResponse(data, 'application/json')
            return JsonResponse(data, safe=False)
        else:
            return render(request, self.template_name)
        


class Consulta(GlobalMixin, ListView):
    template_name = 'transferidos/consulta/general.html'
    context_object_name = 'contribuyentes'
    
    def create_search(self, success, search):

        Busquedas.objects.create(
            busqueda=search,
            usuario=self.request.user.username,
            fecha=datetime.date.today(),
            is_success=success
        )

        return True
        
    
    def get_rfc(self):
    
        search  = self.request.GET.get("kword", '')
        
        if search != '':
      
            self.create_search(True, search)
        
        return search

    def get_queryset(self):
    
        rfc = self.get_rfc()

        kword = self.request.GET.get("kword", '')

        return REC.objects.buscar_rfc(kword)[:1]

    def get_context_data(self, **kwargs):
        context = super(Consulta, self).get_context_data(**kwargs)

        kword = self.request.GET.get("kword", '').strip()

        QuerySet1 = Programa.objects.filter(Q(rfc__icontains = kword) | Q(nombre__icontains = kword)).exclude(estatus='CONCLUIDO')
        QuerySet2 = Programa_Padrones.objects.filter(Q(rfc__icontains = kword) | Q(nombre__icontains = kword)).exclude(estatus='CONCLUIDO')
        QuerySet3 = Programa_Transferidos.objects.filter(Q(rfc__icontains = kword) | Q(nombre__icontains = kword), area="AUDITORIA").exclude(estatus__in=['CONCLUIDO', 'TRANSFERIDO', 'RECHAZADO'])
        QuerySet4 = Programa_Transferidos.objects.filter(Q(rfc__icontains = kword) | Q(nombre__icontains = kword), area="EJECUCION").exclude(estatus__in=['CONCLUIDO', 'TRANSFERIDO', 'RECHAZADO'])
        QuerySet5 = Programa_Transferidos.objects.filter(Q(rfc__icontains = kword) | Q(nombre__icontains = kword), estatus="TRANSFERIDO")

        context['det1'] = QuerySet1
        context['det2'] = QuerySet2
        context['det3'] = QuerySet3
        context['det4'] = QuerySet4
        context['det5'] = QuerySet5
        
        context["paramertro"] = kword

        return context
        

class Get_NoControl(LoginRequiredMixin, ListView):
    model = Programa_Transferidos
    template_name = 'transferidos/auditoria/ver_contribuyente.html'

    def get_en_transferencia(self, rfc):

        QuerySet = Programa_Transferidos.objects.filter(
            rfc__icontains=rfc,
        ).values(
            'nuevo_folio', 'rfc', 'nombre'
        )

        return QuerySet

    def get(self, request, *args, **kwargs):

        # if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
            rfc = self.kwargs.get('rfc')

            if rfc == '':
                data = ''
            else:
                data = list(self.get_en_transferencia(rfc))

            return JsonResponse(data, safe=False)
        else:
            return render(request, self.template_name)
            
            
class Get_Data(LoginRequiredMixin, ListView):
    model = REC
    template_name = 'transferidos/auditoria/ver_contribuyente.html'

    def create_search(self, success):

        Busquedas.objects.create(
            busqueda=self.kwargs.get('rfc'),
            usuario=self.request.user.username,
            fecha=datetime.date.today(),
            is_success=success
        )

        return True

    def get_rfc(self):
        QuerySet = REC.objects.filter(rfc__icontains=self.kwargs.get('rfc'))[:1]
        
        if QuerySet:
            rfc = str(QuerySet[0].rfc)
            self.create_search(True)
        else:
            rfc = ''
            self.create_search(False)
        
        return rfc

    def get_queryset(self, rfc):

        QuerySet = REC.objects.filter(
            rfc__icontains=rfc
        ).values('rfc', 'nombre', 'direccion')

        return QuerySet

    def get_promocion(self, rfc):
        QuerySet = Programa_Padrones.objects.filter(
            # ~Q(seguimiento=''),
            is_active=True,
            rfc__icontains=rfc,
            area = 'PROMOCION'
        ).values(
            'programa','fecha'
        ).exclude(
            estatus='CONCLUIDO'
        )
        return QuerySet

    def get_padrones(self, rfc):

        QuerySet = Programa_Padrones.objects.filter(
            # ~Q(seguimiento=''),
            is_active=True,
            rfc__icontains=rfc,
            area = 'PADRONES'
        ).values(
            'programa','fecha'
        ).exclude(
            estatus='CONCLUIDO'
        )

        return QuerySet

    def get_programacion(self, rfc):

        QuerySet = Programa_Padrones.objects.filter(
            # seguimiento='',
            is_active=True,
            rfc__icontains=rfc,
            area = 'PROGRAMACION'
        ).values(
            'programa','fecha'
        ).exclude(
            estatus='CONCLUIDO'
        )
        return QuerySet

    def get_vigilancia(self, rfc):
    
        QuerySet = Programa.objects.filter(
            rfc__icontains=rfc,
            detalle_programa__estatus='OFICIO'
        ).values(
            'programa','detalle_programa__fecha'
        ).exclude(
            estatus='CONCLUIDO'
        ).exclude(
            folio=''
        )

        # QuerySet = Programa.objects.filter(
            # rfc__icontains=rfc
        # ).values(
            # 'programa','fecha'
        # ).exclude(
            # estatus='CONCLUIDO'
        # ).exclude(
            # folio=''
        # )

        return QuerySet

    def get_auditoria(self, rfc):

        QuerySet = Programa_Transferidos.objects.filter(
            rfc__icontains=rfc,
            area = 'AUDITORIA'
        ).values(
            'programa','fecha'
        ).exclude(
            estatus__in=['CONCLUIDO', 'TRANSFERIDO', 'RECHAZADO']
        )

        return QuerySet

    def get_ejecucion(self, rfc):

        QuerySet = Programa_Transferidos.objects.filter(
            rfc__icontains=rfc,
            area = 'EJECUCION'
        ).values(
            'programa','fecha'
        ).exclude(
            estatus__in=['CONCLUIDO', 'TRANSFERIDO', 'RECHAZADO']
        )

        return QuerySet

    def get_en_transferencia(self, rfc):

        QuerySet = Programa_Transferidos.objects.filter(
            rfc__icontains=rfc,
            estatus="TRANSFERIDO"
        ).values(
            'programa', 'area', 'fecha'
        )

        return QuerySet

    def get(self, request, *args, **kwargs):

        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            rfc = self.get_rfc()
        
            if rfc == '':
                new_rfc = self.kwargs.get('rfc')
                
                data = []
                valor = {'rfc':new_rfc, 'nombre':'*Sin datos', 'direccion':'*Sin datos'}
                data.append(valor)
                
                data.append(list(self.get_padrones(new_rfc)))
                data.append(list(self.get_vigilancia(new_rfc)))
                data.append(list(self.get_auditoria(new_rfc)))
                data.append(list(self.get_ejecucion(new_rfc)))
                data.append(list(self.get_en_transferencia(new_rfc)))
                data.append(list(self.get_programacion(new_rfc)))
                data.append(list(self.get_promocion(new_rfc)))

            else:
                data = list(self.get_queryset(rfc))
                
                data.append(list(self.get_padrones(rfc)))
                data.append(list(self.get_vigilancia(rfc)))
                data.append(list(self.get_auditoria(rfc)))
                data.append(list(self.get_ejecucion(rfc)))
                data.append(list(self.get_en_transferencia(rfc)))
                data.append(list(self.get_programacion(rfc)))
                data.append(list(self.get_promocion(rfc)))

            return JsonResponse(data, safe=False)
        else:
            return render(request, self.template_name)


class Admin_Programacion(CRUDMixin, ListView):
    permission_required = ('view_programa_transferidos')
    
    template_name = 'transferidos/admin_programacion.html'
    context_object_name = 'programacion'

    def get_queryset(self):
        programa_id = self.kwargs.get('id')
        return Programa_Transferidos.objects.filter(id=programa_id)


    def get_context_data(self, **kwargs):
        context = super(Admin_Programacion, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')

        obj_Programa = Programa_Transferidos.objects.filter(id=id)
        
        if Programa.objects.filter(rfc=obj_Programa[0].rfc).exists():
            query_reporte = Programa.objects.filter(rfc=obj_Programa[0].rfc)
        else:
            query_reporte = None
            
        context['reporte'] = query_reporte

        if REC.objects.filter(rfc=obj_Programa[0].rfc).exists():
            obj_REC = REC.objects.filter(rfc=obj_Programa[0].rfc)
            id_contacto = obj_REC[0].id
        else:
            id_contacto = 0

        if Detalle_Transferidos.objects.filter(programa_id = id, estatus__contains='NOTIFICADO').exists():

            if Detalle_Transferidos.objects.filter(programa_id = id, estatus__contains='CONCLUIDO').exists():
                obj_notificado = Detalle_Transferidos.objects.filter(
                    programa_id = id,
                    estatus__contains = 'NOTIFICADO'
                )
                obj_concluido = Detalle_Transferidos.objects.filter(
                    programa_id = id,
                    estatus__contains = 'CONCLUIDO'
                )
                dias = (obj_concluido[0].fecha - obj_notificado[0].fecha).days
            else:
                today = date.today()

                obj = Detalle_Transferidos.objects.filter(
                    programa_id = id,
                    estatus__contains = 'NOTIFICADO'
                )
                dias = (today - obj[0].fecha).days
        else:
            dias = 0

        context['dias'] = dias
        context['detalles'] = Detalle_Transferidos.objects.filter(programa_id = id, is_active=True).exclude(estatus__in=['NUEVO']).order_by('fecha')    
        context['archivos'] = Archivos_Transferidos.objects.filter(programa_id = id, is_active=True)            
        context['pagos_presuntiva'] = Pagos_Transferidos.objects.filter(programa_id = id, presuntiva=True, is_active=True)       
        context['pagos'] = Pagos_Transferidos.objects.filter(programa_id = id, presuntiva=False, is_active=True)      
        context['contactos'] =  Contacto.objects.detalle_all(id_contacto)

        return context    


class Alta_Detalle(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_detalle_transferidos')
    
    model = Detalle_Transferidos
    template_name = 'transferidos/crear/alta_detalle.html'
    form_class = DetalleForm
    success_message = 'Guardado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Alta_Detalle, self).get_context_data(**kwargs)
        context['programa_id'] = self.kwargs['pk']

        user = self.request.user.username
        
        context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE').exclude(comentario='INTEGRACION').order_by('valor')
        context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS').exclude(comentario__in=['CANCELADA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','TRANSFERIDO','VALIDACION', 'RECHAZADO', 'PARA TRANSFERIR']).order_by('id')
        
        return context

    def get_form_kwargs(self):
        kwargs = super(Alta_Detalle, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        
        return kwargs

    def form_valid(self, form):
        #id = form.cleaned_data.get('programa_id')
        id = self.kwargs['pk']
        
        estatus = form.cleaned_data['estatus']
        obj = Codigos_Maestros.objects.filter(id=estatus)
        etapa = form.cleaned_data['etapa']
        obj2 = Codigos_Maestros.objects.filter(id=etapa)
        

        instance = Programa_Transferidos.objects.get(id = str(id))
        instance.etapa = str(obj2[0].comentario)
        instance.estatus = str(obj[0].comentario)
        instance.save()

        form.instance.usuario = self.request.user.username
        form.instance.etapa = str(obj2[0].comentario)
        form.instance.estatus = str(obj[0].comentario)

        return super(Alta_Detalle, self).form_valid(form)

    def get_success_url(self):
        #return reverse_lazy('transferidos_app:admin-programacion-3', kwargs={'id': self.object.programa_id_id })
        return self.request.META['HTTP_REFERER']

class Alta_Pagos(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_pagos_transferidos')
    
    model = Pagos_Transferidos
    template_name = 'transferidos/crear/alta_pagos.html'
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
        return reverse_lazy('transferidos_app:admin-programacion-3', kwargs={'id': self.object.programa_id_id })


class Alta_Archivos(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_archivos_transferidos')
    
    model = Archivos_Transferidos
    template_name = 'transferidos/crear/alta_archivos.html'
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
        return reverse_lazy('transferidos_app:admin-programacion-3', kwargs={'id': self.object.programa_id_id })

class Editar_Detalle(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_detalle_transferidos')
    
    model = Detalle_Transferidos
    template_name = 'transferidos/editar/editar_detalle.html'
    form_class = DetalleForm
    success_message = 'Seguimiento actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Editar_Detalle, self).get_context_data(**kwargs)

        obj = self.get_object()
        
        if self.request.user.area == 'EJECUCION':
            selected_etapa = Codigos_Maestros.objects.filter(codigo='XXSTAGE_EJECUCION', comentario=obj.etapa)
            context['selected_etapa'] = selected_etapa[0].id
            selected_estatus = Codigos_Maestros.objects.filter(codigo='XXSTATUS_EJECUCION', comentario=obj.estatus)
            context['selected_estatus'] = selected_estatus[0].id
        
            context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE_EJECUCION')
            context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS_EJECUCION')
        
        else:
            selected_etapa = Codigos_Maestros.objects.filter(codigo='XXSTAGE', comentario=obj.etapa)
            context['selected_etapa'] = selected_etapa[0].id
            selected_estatus = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario=obj.estatus)
            context['selected_estatus'] = selected_estatus[0].id
            
            context['etapas'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE').exclude(comentario='INTEGRACION')
            context['estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS').exclude(comentario__in=['CANCELADA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA'])
        
        return context

    def get_form_kwargs(self):
        kwargs = super(Editar_Detalle, self).get_form_kwargs()

        obj = Detalle_Transferidos.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id_id)

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
        return reverse_lazy('transferidos_app:admin-programacion-3', kwargs={'id': self.object.programa_id_id })


class Editar_Pago(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_pagos_transferidos')
    
    model = Pagos_Transferidos
    template_name = 'transferidos/editar/editar_pagos.html'
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

        obj = Pagos_Transferidos.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id_id)

        return kwargs

    def get_success_url(self):
        return reverse_lazy('transferidos_app:admin-programacion-3', kwargs={'id': self.object.programa_id_id })
        

class Editar_Archivo(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_archivos_transferidos')
    
    model = Archivos_Transferidos
    template_name = 'transferidos/editar/editar_archivos.html'
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

        obj = Archivos_Transferidos.objects.filter(id=self.kwargs['pk'])
        kwargs['pk'] = str(obj[0].programa_id_id)

        return kwargs 

    def get_success_url(self):
        return reverse_lazy('transferidos_app:admin-programacion-3', kwargs={'id': self.object.programa_id_id })


class Eliminar_Detalle(CRUDMixin, DeleteView):
    permission_required = ('delete_detalle_transferidos')
    
    model = Detalle_Transferidos
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
    permission_required = ('delete_pagos_transferidos')
    
    model = Pagos_Transferidos
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
                
                
class Eliminar_Archivos(CRUDMixin, DeleteView):
    permission_required = ('delete_archivos_transferidos')
    
    model = Archivos_Transferidos
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
                

class Ver_Todo(LoginRequiredMixin, DetailView):
    model = Programa_Transferidos
    template_name = 'transferidos/consulta/ver_todo.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Todo, self).get_context_data(**kwargs)
        id = self.kwargs.get('pk')
      
        context['detalles'] = Detalle_Transferidos.objects.filter(programa_id = id, is_active=True).exclude(estatus__in=['NUEVO','PROPUESTA','FAFD','PRESUNTIVA','OFICIO','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','CANCELADA']).order_by('fecha')     
        context['archivos'] = Archivos_Transferidos.objects.filter(programa_id = id, is_active=True)    
        context['pagos_presuntiva'] = Pagos_Transferidos.objects.filter(programa_id = id, presuntiva=True, is_active=True)      
        context['pagos'] = Pagos_Transferidos.objects.filter(programa_id = id, presuntiva=False, is_active=True)    
        return context      


class Aceptar_Todos(LoginRequiredMixin, FormView):
    template_name = "transferidos/auditoria/aceptar_todos.html"
    form_class = AceptarTodosForm
    success_message = "Aceptados correctamente!"

    def form_valid(self, form):

        id = form.cleaned_data['folio']

        obj = Programa_Transferidos.objects.get(id=id)
        obj.estatus = 'ACEPTADO'
        obj.save()

        Detalle_Transferidos.objects.create(
            programa_id=obj,
            fecha=datetime.date.today(),
            comentarios='',
            estatus='ACEPTADO',
            usuario=self.request.user.username
        )

        # if Programa_Transferidos.objects.filter(nuevo_folio=str(folio)).exists():
        #     lista = Programa_Transferidos.objects.filter(nuevo_folio=str(folio))
        # else:
        #     lista = Programa_Transferidos.objects.filter(id=str(folio))
        
        # for data in lista:
        #     obj = Programa_Transferidos.objects.get(id=data.id)
        #     obj.etapa = 'NUEVO'
        #     obj.estatus = 'NUEVO'
        #     obj.fecha = datetime.date.today()
        #     obj.save()

        #     Detalle_Transferidos.objects.create(
        #         programa_id=obj,
        #         fecha=datetime.date.today(),
        #         comentarios='',
        #         estatus='NUEVO',
        #         usuario=self.request.user.username
        #     )

        return super(Aceptar_Todos, self).form_valid(form)

    def get_success_url(self):
        if self.request.user.area == 'AUDITORIA':
            return reverse_lazy('transferidos_app:lista-auditoria')
        else:
            return reverse_lazy('transferidos_app:lista-ejecucion')   


class Rechazar_Todos(LoginRequiredMixin, FormView):
    template_name = "transferidos/auditoria/rechazar_todos.html"
    form_class = RechazarTodosForm
    success_message = "Rechazados correctamente!"

    def form_valid(self, form):

        folio = form.cleaned_data['folio']

        lista = Programa_Transferidos.objects.filter(nuevo_folio=str(folio))
        
        for data in lista:
            obj = Programa_Transferidos.objects.get(id=data.id)
            obj.estatus = 'RECHAZADO'
            obj.fecha = datetime.date.today()
            obj.save()
            

            Detalle_Transferidos.objects.create(
                programa_id=obj,
                fecha=datetime.date.today(),
                comentarios='',
                estatus='RECHAZADO',
                usuario=self.request.user.username
            )

        return super(Rechazar_Todos, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('transferidos_app:lista-auditoria')  


class Asignar_Auditoria(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "transferidos/auditoria/asignar.html"
    success_url = reverse_lazy('transferidos_app:lista-ejecucion')
    form_class = AsignarAuditoriaForm
    success_message = "Asignado correctamente!"

    def form_valid(self, form):
        seguimiento = form.cleaned_data['seguimiento'] 

        if form.cleaned_data['lista']:
            list_id = form.cleaned_data['lista'].split(',')
            #user = self.request.user.username

            for id in list_id:
                instance = Programa_Transferidos.objects.get(pk=id)
                instance.seguimiento = str(seguimiento)
                instance.save()
                
                # Detalle_Transferidos.objects.create(
                #     programa_id=instance,
                #     fecha=datetime.date.today(),
                #     comentarios='',
                #     estatus='VALIDACION',
                #     usuario=user
                # )                

        return super(Asignar_Auditoria, self).form_valid(form)   


class Asignar_Solicitud(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "transferidos/ejecucion/asignar.html"
    success_url = reverse_lazy('transferidos_app:lista-ejecucion')
    form_class = AsignarAuditoriaForm
    success_message = "Asignado correctamente!"

    def form_valid(self, form):
        seguimiento = form.cleaned_data['seguimiento'] 

        if form.cleaned_data['lista']:
            list_id = form.cleaned_data['lista'].split(',')
            user = self.request.user.username

            for id in list_id:
                instance = Programa.objects.get(pk=id)
                #instance.seguimiento = str(seguimiento)
                instance.estatus = 'SOLICITUD ACEPTADA'
                instance.save()
                
                Detalle.objects.create(
                    programa_id=instance,
                    fecha=datetime.date.today(),
                    comentarios=str(seguimiento),
                    estatus='SOLICITUD ACEPTADA',
                    usuario=user
                )                

        return super(Asignar_Solicitud, self).form_valid(form)  

        
class Ver_Reporte(LoginRequiredMixin, ListView):
    template_name = 'transferidos/auditoria/ver_reporte.html'
    context_object_name = 'programacion'

    def get_queryset(self):
        id = self.kwargs.get('pk')

        queryset = Programa_Transferidos.objects.filter(id = id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Ver_Reporte, self).get_context_data(**kwargs)
        id = self.kwargs.get('pk')

        obj_Programa = Programa_Transferidos.objects.filter(id=id)

        if Programa.objects.filter(rfc=obj_Programa[0].rfc).exists():
            query_reporte = Programa.objects.filter(rfc=obj_Programa[0].rfc)
        else:
            query_reporte = None
            
        context['reporte_vigilancia'] = query_reporte

        if REC.objects.filter(rfc=obj_Programa[0].rfc).exists():
            obj_REC = REC.objects.filter(rfc=obj_Programa[0].rfc)
            id_contacto = obj_REC[0].id
        else:
            id_contacto = 0

        if Detalle_Transferidos.objects.filter(programa_id = id, estatus__contains='NOTIFICADO').exists():

            if Detalle_Transferidos.objects.filter(programa_id = id, estatus__contains='CONCLUIDO').exists():
                obj_notificado = Detalle_Transferidos.objects.filter(
                    programa_id = id,
                    estatus__contains = 'NOTIFICADO'
                )
                obj_concluido = Detalle_Transferidos.objects.filter(
                    programa_id = id,
                    estatus__contains = 'CONCLUIDO'
                )
                dias = (obj_concluido[0].fecha - obj_notificado[0].fecha).days
            else:
                today = date.today()

                obj = Detalle_Transferidos.objects.filter(
                    programa_id = id,
                    estatus__contains = 'NOTIFICADO'
                )
                dias = (today - obj[0].fecha).days
        else:
            dias = 0

        context['dias'] = dias
      
        context['detalles'] = Detalle_Transferidos.objects.filter(programa_id = id, is_active=True).exclude(estatus__in=['NUEVO'])    
        context['archivos'] = Archivos_Transferidos.objects.filter(programa_id = id, is_active=True)    
        context['pagos_presuntiva'] = Pagos_Transferidos.objects.filter(programa_id = id, presuntiva=True, is_active=True)      
        context['pagos'] = Pagos_Transferidos.objects.filter(programa_id = id, presuntiva=False, is_active=True)    
        context['contactos'] =  Contacto.objects.detalle_all(id_contacto)
        return context


class Batch_Ejecucion(LoginRequiredMixin, TemplateView):
    template_name = 'transferidos/batch.html'

    def validar_rfc(self, rfc):
        message = False
        area = ''

        if Programa.objects.filter(~Q(estatus='CONCLUIDO'), rfc__icontains=rfc).exists():
            message = True
            area = 'RECAUDACION'
        if Programa_Padrones.objects.filter(~Q(estatus='CONCLUIDO'), rfc__icontains=rfc).exists():
            message = True
            area = 'RECAUDACION'
        if Programa_Transferidos.objects.filter(~Q(estatus__in=['CONCLUIDO','TRANSFERIDO']), area='AUDITORIA', rfc__icontains=rfc).exists():
            message = True
            area = 'AUDITORIA'
        if Fiscalizados.objects.filter(rfc__icontains=rfc, is_active=True).exists():
            message = True
            area = 'RECAUDACION'
        if Cartas_Invitacion.objects.filter(~Q(estatus__icontains='CONCLUIDO'), rfc__icontains=rfc).exists():
            message = True
            area = 'RECAUDACION'

        return message, area

    def get_context_data(self, **kwargs):
        context = super(Batch_Ejecucion, self).get_context_data(**kwargs)

        context['Formulario'] = BatchForm

        return context

    def post(self, request, *args, **kwargs):
        path = settings.MEDIA_ROOT + '/batch/' + request.FILES['archivo'].name
        path_resp = settings.MEDIA_ROOT + '/batch/'+ request.FILES['archivo'].name[:-4] + '_resp.csv'

        def handle_uploaded_file(file):
            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        def validar_archivo(file):
            with open(path, 'r') as file:
                reader = csv.DictReader(file, delimiter=',', quoting=csv.QUOTE_NONE) 

                for row in reader:
                    row_values = []
                    for field in reader.fieldnames:
                        row_values.append(row[field])
                
                num = reader.line_num
                if int(num) >= 1001:
                    messages.error(self.request, 'El limite son 1000 registros por archivo')
                    return False
                else:
                    return True

        def execute_batch_new(file):

            obj_impuesto = Codigos_Maestros.objects.filter(codigo='XXTAX', id=request.POST.get('programa'))
            impuesto = obj_impuesto[0].comentario

            obj_metodo_envio = Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD_EJECUCION', id=request.POST.get('metodo_envio'))
            metodo_envio = obj_metodo_envio[0].comentario

            user = self.request.user.username

            # Ejecutar Funcion
            cursor = connection.cursor()
            sql = f''' SELECT carga_masiva('{file}', '{user}', '{impuesto}', '{metodo_envio}'); '''
            cursor.execute(sql)

            # Actualizamos tabla Temporal
            #Temporal.objects.filter(estatus = None).update(estatus = 'INSERTADO')
            #data_temporal = Temporal.objects.all()
            #data_temporal.update(programa=impuesto, metodo_envio=metodo_envio)

            # Crear archivo de respuesta
            with open(path_resp, 'w', newline="") as f:
                writer = csv.writer(f)
                writer.writerow(['rfc', 'nombre', 'domicilio', 'programa', 'presuntiva', 'metodo envio','ejercicio','periodo','estatus', 'unidad responsable'])

                for data in Temporal.objects.all().values_list('rfc', 'nombre', 'direccion', 'programa', 'presuntiva', 'metodo_envio', 'ejercicio', 'periodo', 'estatus', 'unidad_responsable'):
                    writer.writerow(data)

            msg = 'Numero de Registros: ' + str(Temporal.objects.all().count()) + '\n' + 'Registros Insertados: ' + str(Temporal.objects.filter(estatus='INSERTADO').count()) + '\n' + 'Registros Excluidos: ' + str(Temporal.objects.filter(estatus='EXCLUIDO').count())
            messages.success(self.request, msg)
            messages.info(self.request, request.FILES['archivo'].name[:-4] + '_resp.csv')


        def execute_batch(file):

            with open(path, 'r') as file:
                reader = csv.DictReader(file, delimiter=',', quoting=csv.QUOTE_NONE) 
                
                lista_contribuyentes = []
                lista_excluidos = []

                obj_impuesto = Codigos_Maestros.objects.filter(codigo='XXTAX', id=request.POST.get('programa'))
                impuesto = obj_impuesto[0].comentario

                obj_metodo_envio = Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD_EJECUCION', id=request.POST.get('metodo_envio'))
                metodo_envio = obj_metodo_envio[0].comentario

                user = self.request.user.username

                for row in reader:
                    row_values = []
                    for field in reader.fieldnames:
                        row_values.append(row[field])
                    
                    flag, area = self.validar_rfc(row_values[0])

                    if flag == False:
                        contribuyente = Programa_Transferidos(
                            rfc=row_values[0],
                            nombre=row_values[1],
                            direccion=row_values[2],
                            programa=impuesto,
                            presuntiva=row_values[3],
                            metodo_envio=metodo_envio,
                            ejercicio=row_values[4],
                            periodo=row_values[5],
                            area='EJECUCION',
                            estatus='ACTIVO',
                            is_active=True,
                            usuario=user,
                            nuevo_folio='1',
                            fecha=datetime.date.today()
                        )
                        lista_contribuyentes.append(contribuyente)
                    else:
                        contribuyente = Programa_Transferidos(
                            rfc=row_values[0],
                            nombre=row_values[1],
                            direccion=row_values[2],
                            programa=impuesto,
                            presuntiva=row_values[3],
                            metodo_envio=metodo_envio,
                            ejercicio=row_values[4],
                            periodo=row_values[5],
                            area=area
                        )
                        lista_excluidos.append(contribuyente)

                Programa_Transferidos.objects.bulk_create(lista_contribuyentes, batch_size=1000)

                with open(path_resp, 'w', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(['rfc', 'nombre', 'domicilio', 'programa', 'presuntiva', 'metodo envio','ejercicio','periodo','estatus', 'unidad responsable'])

                    for row in lista_excluidos:
                        data = []
                        data.append(row.rfc)
                        data.append(row.nombre)
                        data.append(row.direccion)
                        data.append(impuesto)
                        data.append(row.presuntiva)
                        data.append(metodo_envio)
                        data.append(row.ejercicio)
                        data.append(row.periodo)
                        data.append('EXCLUIDO')
                        data.append(row.area)

                        writer.writerow(data)
                    
                    for row in lista_contribuyentes:
                        data = []
                        data.append(row.rfc)
                        data.append(row.nombre)
                        data.append(row.direccion)
                        data.append(impuesto)
                        data.append(row.presuntiva)
                        data.append(metodo_envio)
                        data.append(row.ejercicio)
                        data.append(row.periodo)
                        data.append('INSERTADO')

                        writer.writerow(data)
                            
                msg = 'Numero de Registros: ' + str(reader.line_num - 1) + '\n' + 'Registros Insertados: ' + str(len(lista_contribuyentes)) + '\n' + 'Registros Excluidos: ' + str(len(lista_excluidos))
                
                messages.success(self.request, msg)
                messages.info(self.request, request.FILES['archivo'].name[:-4] + '_resp.csv')
                        

        if request.method == 'POST':
            form = BatchForm(request.POST, request.FILES)
            if form.is_valid():   
                handle_uploaded_file(request.FILES['archivo']) 

                if validar_archivo(request.FILES['archivo']) == False:
                    return redirect(self.request.META['HTTP_REFERER'])

                #execute_batch(request.FILES['archivo'])
                execute_batch_new(request.FILES['archivo'])

                return redirect(self.request.META['HTTP_REFERER'])

        else:
            form = BatchForm()


def DescargarExcel(request, archivo):
    path = settings.MEDIA_ROOT + '/batch/' + archivo

    with open(path, 'rb') as file:
        response = HttpResponse(file.read(),content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)

    return response


class Fecha_Cierre(LoginRequiredMixin, TemplateView):
    template_name = 'transferidos/auditoria/fecha_cierre.html'

    def get_context_data(self, **kwargs):
        context = super(Fecha_Cierre, self).get_context_data(**kwargs)
        
        context['id_programa'] = self.kwargs['pk']
        context['form'] = FechaCierreForm    
        
        return context

    def post(self, request, *args, **kwargs):
        id_programa = self.kwargs['pk']
        
        instance = Programa_Transferidos.objects.get(id = str(id_programa))
        instance.estatus = 'CIERRE'
        instance.save()

        #date_time_str = str(request.POST['fecha'])
        fecha = str(request.POST['fecha'][6:]) + '-' + str(request.POST['fecha'][3:5]) + '-' + str(request.POST['fecha'][0:2])

        Detalle_Transferidos.objects.create(
            programa_id=instance,
            fecha=fecha,
            comentarios=request.POST['comentarios'],
            estatus='CIERRE',
            usuario=self.request.user.username
        )

        return redirect(self.request.META['HTTP_REFERER'])


class ImpuestosView(LoginRequiredMixin, TemplateView):
    template_name = 'transferidos/impuestos.html'

    def get_context_data(self, **kwargs):
        context = super(ImpuestosView, self).get_context_data(**kwargs)

        context['form'] = ImpuestosForm
        context['impuestos'] = Codigos_Maestros.objects.filter(codigo='XXTAX')
        
        return context


class Ver_Impuestos(LoginRequiredMixin, TemplateView):
    template_name = 'transferidos/impuestos.html'

    def get_context_data(self, **kwargs):
        context = super(Ver_Impuestos, self).get_context_data(**kwargs)
        
        # impuesto = Codigos_Maestros.objects.filter(codigo='XXTAX', pk=self.kwargs.get('impuesto'))
        contribuyente = Programa_Transferidos.objects.filter(pk=self.kwargs.get('rfc'))

        context['rfc'] = contribuyente[0].rfc
        context['rfc_id'] = self.kwargs.get('rfc')

        # Obtener la lista de impuestos guardados
        impuestos = Impuestos.objects.values(
            'impuesto'
        ).filter(
            contribuyente = self.kwargs.get('rfc')
        ).distinct()

        lista_impuestos = Codigos_Maestros.objects.filter(
            codigo = 'XXTAX',
            id__in = impuestos
        ).order_by('id')

        value = []
        for row in lista_impuestos:
            value.append(str(row.comentario) + '_' + str(row.id))
        context['lista_impuestos'] = json.dumps(list(value))

        return context


class Admin_Impuestos(View):

    def post(self, request, *args, **kwargs):

        contribuyente = self.kwargs.get('rfc')
        if Programa_Transferidos.objects.filter(rfc=self.request.user.username).exists():
            rfc_generico = Programa_Transferidos.objects.filter(rfc=self.request.user.username).first()
        elif Programa_Transferidos.objects.filter(pk=contribuyente).exists():
            rfc_generico = Programa_Transferidos.objects.filter(pk=contribuyente).first()
        else:
            rfc_generico = 0

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

        # messages.info(self.request, 'en_proceso')
        # messages.success(self.request, 'Impuesto Cargado Exitosamente!')

        # Limpiar impuestos con 0
        impuestos = Impuestos.objects.values(
            'contribuyente'
        ).annotate(
            impuestos=ArrayAgg('impuesto', distinct=True)
        ).filter(
            Q(ejercicio = 1) | Q(ejercicio_1 = 1) | Q(ejercicio_2 = 1) | Q(ejercicio_3 = 1) | Q(ejercicio_4 = 1) | Q(ejercicio_5 = 1),
            contribuyente=rfc_generico
        ).order_by()

        # impuestos = {'contribuyente': 32, 'impuestos': [20, 21, 27, 227]}
        Impuestos.objects.filter(
            contribuyente=rfc_generico
        ).exclude(
            impuesto__in=impuestos[0]['impuestos']
        ).delete()

        return JsonResponse({'result': 'true'})

    def get(self, request, *args, **kwargs):
        # Se genera RFC generico con el username
        contribuyente = self.kwargs.get('rfc')
        impuesto = self.kwargs.get('impuesto')
        
        # Obtener tabla generada
        if impuesto != '0': 
            if Programa_Transferidos.objects.filter(rfc=self.request.user.username).exists():
                rfc_generico = Programa_Transferidos.objects.filter(rfc=self.request.user.username).first()
            elif Programa_Transferidos.objects.filter(pk=contribuyente).exists():
                rfc_generico = Programa_Transferidos.objects.filter(pk=contribuyente).first()
            else:
                rfc_generico = 0

            queryset = Impuestos.objects.filter(
                contribuyente=rfc_generico,
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
                if Programa_Transferidos.objects.filter(rfc=self.request.user.username).exists():
                    instancia_contribuyente = Programa_Transferidos.objects.latest('id')
                elif Programa_Transferidos.objects.filter(pk=contribuyente).exists():
                    instancia_contribuyente = Programa_Transferidos.objects.filter(pk=contribuyente).first()
                else:
                    # Generar registro generico
                    Programa_Transferidos.objects.create(
                        nuevo_folio='',
                        folio='',
                        rfc=self.request.user.username,
                        programa='',
                        presuntiva=0,
                        recaudado=0,
                        dias=0,
                        nombre='',
                        direccion='',
                        fecha=datetime.date.today(),
                        etapa='',
                        estatus='',
                        seguimiento='',
                        usuario='',
                        area='',
                        is_active=False
                    )
                    instancia_contribuyente = Programa_Transferidos.objects.latest('id')
                
                # instancia_contribuyente = Contribuyentes.objects.get(pk=contribuyente)
                instancia_impuesto = Codigos_Maestros.objects.get(pk=impuesto)

                meses = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC']
                bimestres = ['ENE-FEB','MAR-ABR','MAY-JUN','JUL-AGO','SEP-OCT','NOV-DIC']

                lista_mensual = []
                lista_bimestral = []
                lista_anual = []
                ejercicio = datetime.date.today().year

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
                    contribuyente=instancia_contribuyente.id,
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

    def delete(self, request, *args, **kwargs):

        contribuyente = self.kwargs.get('rfc')
        impuesto = self.kwargs.get('impuesto')

        if Programa_Transferidos.objects.filter(rfc=self.request.user.username).exists():
            rfc_generico = Programa_Transferidos.objects.filter(rfc=self.request.user.username).first()
        elif Programa_Transferidos.objects.filter(pk=contribuyente).exists():
            rfc_generico = Programa_Transferidos.objects.filter(pk=contribuyente).first()
        else:
            rfc_generico = 0

        queryset = Impuestos.objects.filter(
            contribuyente=rfc_generico,
            impuesto=impuesto
        ).delete()

        return JsonResponse({'result': 'true'})
        

class LimpiarImpuestos(View):
    
    def delete(self, request, *args, **kwargs):
        
        Programa_Transferidos.objects.filter(
            rfc=self.request.user.username
        ).delete()

        return JsonResponse({'result': 'true'})
        
