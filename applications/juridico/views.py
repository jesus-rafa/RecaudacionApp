import datetime
import json
from queue import Empty
from re import sub
import math
from django.forms.models import BaseModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from applications.users.functions import get_id_user, get_username
from applications.users.mixins import CRUDMixin, GlobalMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import connection
from django.db.models import (Count, DurationField, ExpressionWrapper, F,
                              IntegerField, Q, Subquery, Sum, Value)
from django.db.models.functions import Coalesce
from django.http.response import JsonResponse
from django.shortcuts import HttpResponse, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, View)
from django.views.generic.edit import UpdateView

from .forms import (Form_Demanda, Form_Edita_Demanda, Form_Solicitante, Form_Resolutor, Form_ResolutorDetalle, Form_Requisito,Form_ResolutorArchivo)
from .models import (Archivos_Juridico, Catalogo, Demanda, Formulario, Proceso,
                     Proceso_Detalle, Rubros, User, Solicitante, Resolutor, Resolutor_detalle, Requisitos)
from .functions import get_carpeta
from .serializers import Solicitante_Serialize
from rest_framework.generics import ListAPIView
from django.template.loader import get_template 
import subprocess


# Create your views here.
class Demanda_View(GlobalMixin,ListView):
    template_name = 'juridico/panel_juridico.html'
    model = Demanda
    context_object_name = 'demanda'

    def get_queryset(self):
        queryset = Demanda.objects.filter(is_active=True,created__gt = datetime.date(2023, 5, 31))  # .order_by('id')
        queryset = queryset.annotate(days=(ExpressionWrapper(
            F('fecha_interno') - datetime.date.today(), output_field=DurationField())), orden = (ExpressionWrapper(
            F('created') - datetime.date.today(), output_field=DurationField()))).order_by('days')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Demanda_View, self).get_context_data(**kwargs)
        # hoy = datetime.date.today()
        # hoy = hoy.strftime("%d/%m/%Y")
        # context['hoy'] = hoy
        # context['hoys'] = Demanda.objects.all().annotate(days=(ExpressionWrapper(
        #     hoy - F('fecha_interno'), output_field=DurationField()))).order_by('days')
        demanda = Demanda.objects.all()
        if demanda:
            context['last_folio'] = Demanda.objects.latest('created')
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        context['tomorrow'] = tomorrow
        context['today'] = today
        context['creados_hoy'] = Demanda.objects.filter(created__gte = today,created__lt = tomorrow, is_active=True).annotate(days=(ExpressionWrapper(
            F('fecha_interno') - datetime.date.today(), output_field=DurationField())), orden = (ExpressionWrapper(
            F('created') - datetime.date.today(), output_field=DurationField()))).order_by('orden')
        if context['creados_hoy']:
            existe = 1
        else:
            existe = 0

        context['existe'] = existe
        context['orderer'] = context['creados_hoy'] | context['demanda']

        return context


class Alta_Demanda(SuccessMessageMixin, CreateView):
    model = Demanda
    template_name = 'juridico/crear/alta_demanda.html'
    form_class = Form_Demanda

    def get_context_data(self, **kwargs):
        context = super(Alta_Demanda, self).get_context_data(**kwargs)
        context['juicio'] = Catalogo.objects.filter(agrupador='SELECT_JUICIO')
        context['subtipo'] = Catalogo.objects.filter(
            agrupador='SELECT_SUBTIPO')
        result = Rubros.objects.values(
            'id', 'nombre', 'interno', 'fatal', 'agrupador')
        context['procesos'] = json.dumps(list(result))
        tribu = Catalogo.objects.values('id','nombre','valor').filter(agrupador='SELECT_TRIBUNAL')
        context['tribunal'] = json.dumps(list(tribu))


        return context

    # def get_initial(self):
    #     carpeta = get_carpeta()
    #     return {
    #         "carpeta": carpeta
    #     }

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        carpeta_consecutivo = get_carpeta(form)
        form.instance.carpeta = carpeta_consecutivo
        messages.success(self.request, 'Se creo la carpeta: ' + str(carpeta_consecutivo))

        return super(Alta_Demanda, self).form_valid(form)

    def get_success_url(self):
        # Redireccionamos a la vista principal 'leer'
        return reverse('juridico_app:juridico')


class Edita_Demanda(SuccessMessageMixin, UpdateView):
    model = Demanda
    template_name = 'juridico/editar/edita_demanda.html'
    form_class = Form_Edita_Demanda

    success_message = 'Registro actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Edita_Demanda, self).get_context_data(**kwargs)
        tribu = Catalogo.objects.values('id','nombre','valor').filter(agrupador='SELECT_TRIBUNAL')
        context['tribunal'] = json.dumps(list(tribu))
        return context


    def get_success_url(self):
        # Redireccionamos a la vista principal 'leer'
        return reverse('juridico_app:juridico')

class Detalle_Demanda(ListView):
    template_name = 'juridico/consultar/detalle_demanda.html'
    context_object_name = 'detalleDemanda'

    def get_queryset(self):
        id_demanda = self.kwargs.get('id')
        return Demanda.objects.filter(id=id_demanda)

    def get_context_data(self, **kwargs):
        context = super(Detalle_Demanda, self).get_context_data(**kwargs)

        # idDesarrollo = self.kwargs.get('id')
        id_demanda = self.kwargs.get('id')

        # context['idDesarrollo'] = idDesarrollo

        # context['forms'] = Formulario.objects.filter(detalle_id=idDesarrollo)
        context['procesal'] = Proceso.objects.filter(demanda = id_demanda).order_by('-created')
        #context['opcion'] = Catalogo.objects.filter(agrupador="SELECT_PROCESO")
        context['demanda'] = id_demanda

        demanda = Demanda.objects.values('juicio','subtipo').filter(id=id_demanda)
        demandaTipo = str(demanda[0]['juicio']) + '_' + str(demanda[0]['subtipo'])

        context['opcion'] = Rubros.objects.filter(~Q(formulario = None),agrupador=demandaTipo, ).order_by('sort')

        return context


# Administar Demanda
class Admin_Demanda(LoginRequiredMixin, TemplateView):
    template_name = 'juridico/admin_demanda.html'

    def get_context_data(self, **kwargs):
        context = super(Admin_Demanda, self).get_context_data(**kwargs)

        id_demanda = self.kwargs.get('pk')

        context['detalleDemanda'] = Demanda.objects.filter(
            id=id_demanda
        )
        demanda = Demanda.objects.values(
            'juicio',
            'subtipo'
        ).filter(
            id=id_demanda
        )
        #demandaTipo = str(demanda[0]['juicio']) + str(demanda[0]['subtipo'])
        demandaTipo = str(demanda[0]['juicio']) + '_' + str(demanda[0]['subtipo'])
        # context['opcion'] = Rubros.objects.filter(
        #     agrupador=demandaTipo
        # ).order_by('sort')
        demandaEtapa = Demanda.objects.values('estado_procesal').filter(id=id_demanda)
        demandaEtapa = demandaEtapa[0]['estado_procesal'] + 1
        # if demandaEtapa == 2:
        #     context['opcion'] = Rubros.objects.filter(~Q(formulario = 0),agrupador=demandaTipo).order_by('sort')
        #     # context['opcion'] = Rubros.objects.filter(~Q(formulario = 0),agrupador=demandaTipo, etapa__in = (2,3)).order_by('sort')
        # else:
        #     context['opcion'] = Rubros.objects.filter(~Q(formulario = 0),agrupador=demandaTipo, etapa = demandaEtapa ).order_by('sort')
        context['opcion'] = Rubros.objects.filter(~Q(formulario = 0),agrupador=demandaTipo).order_by('id')                                                         

        context['demanda'] = id_demanda

        # context['procesos'] = Proceso.objects.filter(
        #     demanda=id_demanda
        # ).order_by('-rubro_id') #.distinct('rubro_id')

        context['etapa_1'] = Proceso.objects.filter(
            ( Q(demanda=id_demanda,etapa=1) | 
            Q(demanda=id_demanda,etapa=2) ), is_active = True
        ).order_by('-rubro_id')

        context['etapa_2'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=3,
            is_active = True
        ).order_by('-rubro_id')

        context['etapa_3'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=4,
            is_active = True
        ).exclude(rubro__formulario__in = (3,4,5,6,7,8,10,11,12,13)).order_by('created')

        context['segunda_instancia'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=4,
            padre__isnull=False
        ).exclude(rubro__formulario__in = (3,4,5,6,7,8,13)).order_by('rubro_id')

        context['etapa_4'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=5
        ).order_by('-rubro_id')
        
        context['suspension'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=4,
            rubro__formulario = 3
        ).order_by('-id')

        context['cautelares'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=4,
            rubro__formulario = 4
        ).order_by('-id')

        context['reclamacion'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=4,
            rubro__formulario__in = (5,6)
        ).order_by('-id')

        context['incidentes'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=4,
            rubro__formulario = 7
        ).order_by('-id')

        context['periciales'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=4,
            rubro__formulario = 8
        ).order_by('-id')

        context['quejas'] = Proceso.objects.filter(
            demanda=id_demanda,
            etapa=4,
            rubro__formulario = 13
        ).order_by('-id')
        # Subconsulta para contar la cantidad de archivos por proceso
        context['hoy'] = datetime.date.today()
        return context


class Ver_Detalle_Demanda(DetailView):
    model = Demanda
    template_name = 'juridico/consultar/ver_detalle_demanda.html'
    form_class = Form_Demanda
    context_object_name = 'verDemanda'

    def get_context_data(self, **kwargs):
        context = super(Ver_Detalle_Demanda, self).get_context_data(**kwargs)
        #context['procesal'] = Proceso.objects.filter(demanda = self.kwargs.get('pk')).order_by('-created')[:5]
        #procesoT = Proceso.objects.filter(demanda = self.kwargs.get('pk')).order_by('-created')[:5]
        #instancia_proceso = Proceso.objects.get(demanda = self.kwargs.get('pk'))[:1]
        #context['instancia_proceso'] = Demanda.objects.filter(juicio=9).values('carpeta').order_by('-id')[:1]
        context['procesal1'] = Proceso_Detalle.objects.filter(dato = 'comentario', id_proceso__demanda = self.kwargs.get('pk') ).order_by('-folio').distinct('folio')[:5]
        proceso = Proceso.objects.filter(demanda = self.kwargs.get('pk')).order_by('etapa_id').distinct('etapa_id')
        context['proceso_last'] = Proceso.objects.filter(demanda = self.kwargs.get('pk')).last()
        if len(proceso) > 1 :
            context['procesal_Seguimiento'] = Proceso.objects.filter(demanda = self.kwargs.get('pk')).order_by('etapa_id').distinct('etapa_id').exclude(etapa_id = 1)
            context['procesal_Seguimiento_Activo'] = Proceso.objects.filter(demanda = self.kwargs.get('pk')).order_by('-etapa_id').distinct('etapa_id').exclude(etapa_id = 1)[:1]
        else:
            context['procesal_Seguimiento'] = None
            context['procesal_Seguimiento_Activo'] = Proceso.objects.filter(demanda = self.kwargs.get('pk')).order_by('-etapa_id').distinct('etapa_id').exclude(etapa_id = 1)[:1]
        #procesos = Proceso.objects.values('etapa_id','etapa.nombre').filter(demanda = self.kwargs.get('pk')).order_by('procesal_id').distinct('procesal_id')
        #etapas = Catalogo.objects.values('id','nombre').filter(agrupador = 'ESTADO_PROCESAL').order_by('id')
        #context['etapas'] = Catalogo.objects.filter(agrupador = 'ESTADO_PROCESAL')
        # queryset = Demanda.objects.get(pk=self.get_object())
        # queryset = queryset.annotate(days=(ExpressionWrapper(F('fecha_interno') - datetime.date.today(), output_field=DurationField()))).order_by('days')
        # context['dias_restantes'] = queryset.days
        # print(context['dias_restantes'])
        # queryset = queryset.annotate(days=(ExpressionWrapper(F('fecha_interno') - datetime.date.today(), output_field=DurationField()))).order_by('days')
        context['etapas_secundarias'] = Proceso.objects.filter(rubro__formulario__in = (3,4,5,6,7,8,13)).order_by('rubro_id').distinct('rubro_id')
        if not proceso:
            context['etapas'] = Catalogo.objects.filter(
                agrupador='ESTADO_PROCESAL')
        else:
            cursor = connection.cursor()
            sql = f''' select distinct
                            c.id ,c.nombre
                        from
                            public.juridico_catalogo c
                            join public.juridico_proceso p
                            on c.id <> p.etapa_id
                        where
                            c.agrupador = 'ESTADO_PROCESAL'
                            and P.demanda_id =  {self.kwargs.get('pk')}
                            and c.id not in (select etapa_id from public.juridico_proceso where demanda_id =  {self.kwargs.get('pk')} )
                            and c.id not in (3,1)
                        order by id '''
            print(sql)
            cursor.execute(sql)
            fieldnames = [name[0] for name in cursor.description]
            result = []
            for row in cursor.fetchall():
                rowset = []
                for field in zip(fieldnames, row):
                    rowset.append(field)
                result.append(dict(rowset))

            context['etapas'] = result
            print(context['etapas'])
        return context


class Alta_Formulario(LoginRequiredMixin, TemplateView):
    template_name = 'juridico/crear/alta_formularioGenerico.html'

    def get_context_data(self, **kwargs):
        context = super(Alta_Formulario, self).get_context_data(**kwargs)

        idEstadoDetalle = self.kwargs.get('formulario_id')
        id_demanda = self.kwargs.get('demanda')
        if self.kwargs.get('padre') != 0:
            id_padre = self.kwargs.get('padre')
        else:            
            id_padre = 0
        id_rubro = self.kwargs.get('rubro')

        nombre_proceso = Rubros.objects.filter(formulario=idEstadoDetalle).values('nombre')

        context['formulario'] = Formulario.objects.filter(plantilla_form=idEstadoDetalle)

        context['proceso'] = nombre_proceso[0]['nombre']

        #context['opcion'] = Rubros.objects.all().order_by('sort')

        context['opcion'] = Catalogo.objects.all().order_by('sort')

        context['demanda'] = id_demanda

        context['demanda_instance'] = Demanda.objects.get(pk=id_demanda)
        
        context['padre'] = id_padre

        context['rubro'] = id_rubro

        demanda = Demanda.objects.values(
            'juicio', 'subtipo'
        ).filter(id=id_demanda)

        context['demandaTipo'] = str(
            demanda[0]['juicio']) + str(demanda[0]['subtipo']

                                        )
        return context

    def post(self, request, *args, **kwargs):

        def get_folio():
            try:
                last_folio = Proceso_Detalle.objects.latest('folio')
                folio = int(str(last_folio)) + 1
            except:
                folio = 1

            return folio

        def calculo_dias(notificacion,proceso):
            cursor = connection.cursor()
            sql = f'''SELECT public.fechas_juridico_proceso('{notificacion}','{proceso}')'''
            print(sql)
            cursor.execute(sql)
            fieldnames = [name[0] for name in cursor.description]
            result = []
            for row in cursor.fetchall():
                rowset = []
                for field in zip(fieldnames, row):
                    rowset.append(field)
                result.append(dict(rowset))
            query = result

            # return JsonResponse({'res': query [0]['dias_habiles']})
            return query[0]['fechas_juridico_proceso'] #JsonResponse({'res': query[0]['fechas_juridico_proceso']})



        idEstadoDetalle = self.kwargs.get('formulario_id')
        idDemanda = self.kwargs.get('demanda')
        if self.kwargs.get('padre') != 0:
            id_padre = self.kwargs.get('padre')
        else:            
            id_padre = 0
        id_rubro = self.kwargs.get('rubro')
        usuario = User.objects.get(id=self.request.user.id)
        folio = get_folio()
        instancia_demanda = Demanda.objects.get(pk=idDemanda)


        if request.method == 'POST':
            FormData = request.POST

            for key, value in FormData.items():
                if key != 'csrfmiddlewaretoken':
                    if idEstadoDetalle == 1:
                        if key == 'date_contestacion':
                            if not value is None and value != '':
                                fecha = datetime.datetime.strptime(
                                    value, '%d/%m/%Y').strftime('%Y-%m-%d')
                                instancia_demanda.fecha_contestacion = fecha
                        elif key == 'oficio_contestacion':
                            instancia_demanda.oficio = value

            instancia_demanda.save()
            rubro = Rubros.objects.get(pk = id_rubro) #agrupador = str(instancia_demanda.juicio_id) + '_' + str(instancia_demanda.subtipo_id) , formulario = idEstadoDetalle )
            usuario = User.objects.get(pk = get_id_user(self))
            etapa = Catalogo.objects.get(pk = rubro.etapa_id)

            ultimo_proceso = Proceso.objects.filter(demanda=idDemanda).order_by('-created')[:1]
            instancia_actualiza_proceso = Proceso.objects.get(id=ultimo_proceso[0].id)
            instancia_actualiza_proceso.fecha_cierre = datetime.date.today()
            instancia_actualiza_proceso.save()

            fechas = calculo_dias(instancia_demanda.fecha_notificacion,rubro.id)
            fechas = fechas.replace(')','').replace('(','').split(',')

            if id_padre == 0 :
                Proceso.objects.create(
                    demanda=instancia_demanda, 
                    etapa=etapa, 
                    rubro=rubro, 
                    created_by=usuario,
                    fecha_interno=fechas[0],
                    fecha_fatal=fechas[1],
                ).save()
            else:
                instancia_proceso_padre = Proceso.objects.get(pk=id_padre)
                Proceso.objects.create(
                    demanda=instancia_demanda, 
                    etapa=etapa, 
                    rubro=rubro, 
                    created_by=usuario,
                    fecha_interno=fechas[0],
                    fecha_fatal=fechas[1],
                    padre = instancia_proceso_padre
                ).save()

            instancia_proceso = Proceso.objects.get(
                pk=str(Proceso.objects.last())
            )

            for key, value in FormData.items():
                if key != 'csrfmiddlewaretoken':
                    Proceso_Detalle.objects.create(
                        folio=folio,
                        id_proceso=instancia_proceso,
                        dato=key,
                        valor=value,
                        created_by=usuario
                    )
            
            Demanda.objects.filter(id=idDemanda).update(estado_procesal=rubro.etapa_siguiente)
            
            messages.success(self.request, 'Datos Guardados')

        return redirect(self.request.META['HTTP_REFERER'])


class PlantillaView(View):

    def get(self, request, *args, **kwargs):

        id_juicio = self.kwargs.get('id_juicio')
        id_subtipo = self.kwargs.get('id_subtipo')
        fecha_notificacion = self.kwargs.get('fecha_notificacion')
        self.kwargs.setdefault('fecha_aviso', 'NA')

        if (self.kwargs.get('fecha_aviso', 'NA') == 'NA'):
            fecha_aviso = 'null'
        else:
            fecha_aviso = "'" + str(self.kwargs.get('fecha_aviso')) + "'"

        cursor = connection.cursor()
        sql = f'''SELECT public.fechas_juridico('{id_juicio}','{id_subtipo}','{fecha_notificacion}',{fecha_aviso})'''
        print(sql)
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        query = result

        # return JsonResponse({'res': query [0]['dias_habiles']})
        return JsonResponse({'res': query[0]['fechas_juridico']})


class InicioEjecucionView(GlobalMixin, ListView):
    """ vista que carga la pagina de inicio """
    template_name = 'home/inicio_juridico.html'
    # login_url = reverse_lazy('users_app:login')
    context_object_name = 'recaudado'

    def get_queryset(self):
        QuerySet = None
        return QuerySet


class Eliminar_Archivo(View):

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        instancia = Archivos_Juridico.objects.get(pk=pk)
        instancia.delete()

        return JsonResponse({'res': 'ok'})


class Get_Files(DetailView):

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get('pk')

        data = []
        lista = []
        for row in Archivos_Juridico.objects.filter(proceso=pk):
            data_file = {}
            data_file['id'] = row.id
            data_file['url'] = '/media/juridico' + row.archivo.name[8:]
            data_file['nombre'] = row.archivo.name[8:]
            data_file['size'] = row.archivo.size
            lista.append(data_file)

        data = json.dumps(lista)

        return HttpResponse(data, 'application/json')

    def get_context_data(self, **kwargs):
        context = super(Get_Files, self).get_context_data(**kwargs)
        
        context['opcion'] = Archivos_Juridico.objects.all().order_by('sort')


        return context


class Subir_Archivos(TemplateView):
    template_name = 'juridico/subir_archivos.html'

    def get_context_data(self, **kwargs):
        context = super(Subir_Archivos, self).get_context_data(**kwargs)

        pk = self.kwargs.get('pk')

        context['pk'] = pk

        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        instancia = Proceso.objects.get(pk=pk)

        archivo = request.FILES['file']

        Archivos_Juridico(
            proceso=instancia,
            archivo=archivo
        ).save()

        return JsonResponse({'res': 'ok'})
        

class Ver_Detalle_Proceso(LoginRequiredMixin, TemplateView):
    template_name = 'juridico/consultar/ver_formulario_generico.html'

    # def get_context_data(self, **kwargs):
    #     context = super(Ver_Detalle_Proceso, self).get_context_data(**kwargs)

    #     id_proceso = self.kwargs.get('id_proceso')

    #     context['ver_detalle_proceso'] = Proceso_Detalle.objects.filter(
    #         id_proceso = id_proceso
    #     ).order_by('folio')

    #     print(context['ver_detalle_proceso'])

    #     return context
    #template_name = 'juridico/editar/edita_formularioGenerico.html'

    def get_instance(self):
        queryset = Proceso_Detalle.objects.filter(
            id_proceso = self.kwargs.get('proceso')
        ).order_by('folio')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Ver_Detalle_Proceso, self).get_context_data(**kwargs)

        proceso = self.kwargs.get('proceso')
        formulario = self.kwargs.get('formulario')

        nombre_proceso = Rubros.objects.filter(formulario=formulario).values('nombre')

        context['formulario'] = Formulario.objects.filter(plantilla_form=formulario)

        context['proceso'] = nombre_proceso[0]['nombre']

        #context['opcion'] = Rubros.objects.all().order_by('sort')

        context['opcion'] = Catalogo.objects.all().order_by('sort')

        context['proceso_id'] = proceso
        context['formulario_id'] = formulario

        #context['folio'] = Proceso_Detalle.objects.filter(id_proceso=proceso).order_by('folio').values('folio')

        context['ver_detalle_proceso'] = self.get_instance()


        return context

class Actualiza_Detalle_Proceso(LoginRequiredMixin, TemplateView):
    template_name = 'juridico/editar/edita_formularioGenerico.html'

    def get_instance(self):
        queryset = Proceso_Detalle.objects.filter(
            id_proceso = self.kwargs.get('proceso')
        ).order_by('folio')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Actualiza_Detalle_Proceso, self).get_context_data(**kwargs)

        proceso = self.kwargs.get('proceso')
        formulario = self.kwargs.get('formulario')

        nombre_proceso = Rubros.objects.filter(formulario=formulario).values('nombre')

        context['formulario'] = Formulario.objects.filter(plantilla_form=formulario)

        context['proceso'] = nombre_proceso[0]['nombre']

        #context['opcion'] = Rubros.objects.all().order_by('sort')

        context['opcion'] = Catalogo.objects.all().order_by('sort')

        context['proceso_id'] = proceso
        context['formulario_id'] = formulario

        #context['folio'] = Proceso_Detalle.objects.filter(id_proceso=proceso).order_by('folio').values('folio')

        context['ver_detalle_proceso'] = self.get_instance()


        return context

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            FormData = request.POST

            instance = self.get_instance()

            for campo in instance:
                obj = Proceso_Detalle.objects.get(id=campo.id)

                for key, value in FormData.items():
                    if obj.dato == key:
                        obj.valor = value
                        obj.save()

            messages.success(self.request, '¡Actualizado!')

        return redirect(self.request.META['HTTP_REFERER'])
        
class Elimina_Demanda(View):

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        instancia = Demanda.objects.get(pk=pk)
        instancia.is_active = False
        instancia.save()

        messages.success(self.request, '¡Registro eliminado!')

        return redirect(self.request.META['HTTP_REFERER'])
    
class Computo_Proceso(View):

    def get(self, request, *args, **kwargs):
        proceso = self.kwargs.get('proceso')
        notificacion = self.kwargs.get('notificacion')

        cursor = connection.cursor()
        sql = f'''SELECT public.fechas_juridico_proceso('{notificacion}','{proceso}')'''
        print(sql)
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        query = result

        # return JsonResponse({'res': query [0]['dias_habiles']})
        return JsonResponse({'res': query[0]['fechas_juridico_proceso']})  #query[0]['fechas_juridico_proceso'] #JsonResponse({'res': query[0]['fechas_juridico_proceso']})

def Elimina_Proceso(request):
    pk = request.GET.get('pk')

    instancia = Proceso.objects.get(pk=pk)
    instancia.is_active = False
    instancia.save()

    #request.messages.success('¡Registro eliminado!')

    return JsonResponse({'result': 'ok'})

def demanda_page(request):
    template_name = 'juridico/admin_demandacopy.html'
    return render(request, template_name)

def demanda_json(request):
    #demanda_json
    persons = Demanda.objects.all()
    total = persons.count()

    _start = request.GET.get('start')
    _length = request.GET.get('length')
    if _start and _length:
        start = int(_start)
        length = int(_length)
        page = math.ceil(start / length) + 1
        per_page = length

        persons = persons[start:start + length]

    data = [person.to_dict_json() for person in persons]
    response = {
        'data': data,
        'page': page,  # [opcional]
        'per_page': per_page,  # [opcional]
        'recordsTotal': total,
        'recordsFiltered': total,
    }
    return JsonResponse(response)

class Expediente(LoginRequiredMixin, TemplateView):
    template_name = 'juridico/consultar/expediente_modal.html'

    def get_context_data(self, **kwargs):
        context = super(Expediente, self).get_context_data(**kwargs)

        #context['total_registros'] = REC.objects.all().count()

        return context

#                                                 __^__                                      __^__
#                                                ( ___ )------------------------------------( ___ )
#                                                 | / |               RESOLUTOR              | \ |
#                                                (_____)------------------------------------(_____) 
""" SOLICITANTE """
class Solicitantes(CreateView):
    template_name = 'juridico/resolutor/crear/alta_resolutor.html'
    form_class = Form_Solicitante
    #Form_Solicitante
    def get_context_data(self, **kwargs):
        context = super(Solicitantes, self).get_context_data(**kwargs)
        context['form_res'] = Form_Resolutor
        return context
    
    def get_success_url(self):
        return reverse('juridico_app:alta_solicitante')

class SolicitanteActualiza(UpdateView):
    model = Solicitante
    template_name = 'juridico/resolutor/actualizar/solicitanteAndResolutor.html'
    form_class = Form_Solicitante
    success_url = reverse_lazy('juridico_app:panel-resolutor')
    success_message = "Registro actualizado exitosamente!"

    def get_context_data(self, **kwargs):
        context = super(SolicitanteActualiza, self).get_context_data(**kwargs)
    
        context['form_res'] = Form_Resolutor
        return context

class ResolutorActualiza(UpdateView):
    model = Resolutor
    template_name = 'juridico/resolutor/actualizar/solicitanteAndResolutor.html'
    form_class = Form_Resolutor

    def get_context_data(self, **kwargs):
        context = super(ResolutorActualiza, self).get_context_data(**kwargs)
    
        context['form_res'] = Form_Solicitante
        return context
    
    def get_success_url(self):
        # Redireccionamos a la vista principal 'leer'
        messages.success(self.request, 'Se creo resolutor')
        return reverse_lazy('juridico_app:panel-resolutor')  

""" RESOLUTORES """
class Resolutores(CreateView):
    template_name = 'juridico/resolutor/crear/alta_resolutor.html'
    form_class = Form_Resolutor

    def get_success_url(self):
        # Redireccionamos a la vista principal 'leer'
        messages.success(self.request, 'Se creo resolutor')
        return reverse_lazy('juridico_app:panel-resolutor')      

""" RESOLUTOR DETALLE """
class Resolutor_Revision(TemplateView):
    template_name = "juridico/resolutor/consultar/revision.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        completo = True
        context = super(Resolutor_Revision, self).get_context_data(**kwargs)
        etapa = Catalogo.objects.get(nombre="DOCUMENTACION")
        aceptado = Catalogo.objects.get(nombre="ACEPTADO")
        context['id'] = pk
        context['creacion'] = Catalogo.objects.get(nombre="Creacion")
        context['aceptado'] = aceptado
        context['rechazado'] = Catalogo.objects.get(nombre="RECHAZADO")
        context['usuario_id'] = self.request.user.id
        context['detalle'] = Resolutor.objects.get(pk = pk)
        context['detalle_tab'] = Resolutor_detalle.objects.filter(resolutor_id = pk,activo = True).exclude(estatus=188).order_by('-id')
        context['archivos'] = Resolutor_detalle.objects.filter(resolutor = pk,activo = True,etapa=etapa).order_by('-id')
        context['formArchivos'] = Form_ResolutorArchivo
        requisitos = Resolutor_detalle.objects.filter(resolutor=pk, activo=True, requisito__obligatorio=True, etapa = etapa).order_by("-id")
        for req in requisitos:
            if req.estatus != aceptado:
                completo = False
        context['completo'] = completo
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Hecho')
        return reverse('juridico_app:panel-resolutor')
    
class Resolutor_AltaReporte(UpdateView):
    model = Resolutor_detalle
    form_class = Form_ResolutorArchivo
    template_name = "juridico/resolutor/crear/alta_reportes.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        context = super(Resolutor_AltaReporte, self).get_context_data(**kwargs)
        context['pk'] = pk
        resolutor = Resolutor_detalle.objects.get(pk=pk).resolutor
        context['detalle'] = Resolutor.objects.get(pk = resolutor.id)
        concluido = Catalogo.objects.get(nombre="Concluido")
        #context['archivo'] = Resolutor_detalle.objects.get(resolutor = pk, estatus = concluido, etapa)
        return context
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        etapa = Catalogo.objects.get(nombre="Concluido")
        pk = self.kwargs.get('pk')
        resolutor = Resolutor_detalle.objects.get(pk=pk).resolutor
        form.instance.estatus = etapa 
        form.instance.etapa = etapa 
        form.instance.resolutor_id =  resolutor.id
        form.instance.usuario_id = self.request.user.id
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Hecho')
        return reverse('juridico_app:panel-resolutor')

class Resolutor_AltaDetalle(CreateView):
    model = Resolutor_detalle
    #fields = ['resolutor','etapa','estatus','comentarios','usuario']
    form_class = Form_ResolutorDetalle
    template_name = "juridico/resolutor/consultar/revision.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        completo = True
        context = super(Resolutor_AltaDetalle, self).get_context_data(**kwargs)
        etapa = Catalogo.objects.get(nombre="DOCUMENTACION")
        aceptado = Catalogo.objects.get(nombre="ACEPTADO")
        context['id'] = pk
        context['creacion'] = Catalogo.objects.get(nombre="Creacion")
        context['aceptado'] = aceptado
        context['rechazado'] = Catalogo.objects.get(nombre="RECHAZADO")
        context['usuario_id'] = self.request.user.id
        context['detalle'] = Resolutor.objects.get(pk = pk)
        context['detalle_tab'] = Resolutor_detalle.objects.filter(resolutor_id = pk,activo = True).exclude(estatus=188).order_by('-id')
        context['archivos'] = Resolutor_detalle.objects.filter(resolutor = pk,activo = True,etapa=etapa).order_by('-id')
        context['formArchivos'] = Form_ResolutorArchivo
        requisitos = Resolutor_detalle.objects.filter(resolutor=pk, activo=True, requisito__obligatorio=True, etapa = etapa).order_by("-id")
        for req in requisitos:
            if req.estatus != aceptado:
                completo = False
        context['completo'] = completo
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Hecho')
        return reverse('juridico_app:panel-resolutor')
    
class Resolutor_AltaArchivo(UpdateView):
    model = Resolutor_detalle
    form_class = Form_ResolutorArchivo
    template_name = "juridico/resolutor/actualizar/requisito_detalle.html"

    def get_context_data(self, **kwargs):
        context = super(Resolutor_AltaArchivo, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['fk'] = self.kwargs.get('fk')
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Hecho')
        return reverse('juridico_app:resolutorDetalle',args=[self.kwargs.get('fk')])
        #return redirect(url)

class Resolutor_AltaArchivoEjecucion(UpdateView):
    model = Resolutor_detalle
    form_class = Form_ResolutorArchivo
    template_name = "juridico/resolutor/actualizar/requisito_detalle.html"

    def get_context_data(self, **kwargs):
        context = super(Resolutor_AltaArchivo, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        context['fk'] = self.kwargs.get('fk')
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Hecho')
        return reverse('juridico_app:resolutorEjecucion',args=[self.kwargs.get('fk')])
        #return redirect(url)
    
class Resolutor_lectura(ListView):
    model = Resolutor_detalle
    template_name = "juridico/resolutor/consultar/resolutor_lectura.html"
    context_object_name = "listado_resolutor"

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        etapa = Catalogo.objects.get(nombre="DOCUMENTACION")
        queryset = Resolutor_detalle.objects.filter(resolutor=pk, etapa=etapa).order_by("-id")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(Resolutor_lectura, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['creacion'] = Catalogo.objects.get(nombre="Creacion")
        context['aceptado'] = Catalogo.objects.get(nombre="ACEPTADO")
        context['rechazado'] = Catalogo.objects.get(nombre="RECHAZADO")
        context['resolutor'] = Resolutor.objects.get(pk = pk)
        return context
    
class Resolutor_detalleList(ListView):
    model = Resolutor_detalle
    template_name = "juridico/resolutor/consultar/resolutor_detalle.html"
    context_object_name = "listado_resolutor"

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        etapa = Catalogo.objects.get(nombre="DOCUMENTACION")
        queryset = Resolutor_detalle.objects.filter(resolutor=pk, activo=True, etapa=etapa).order_by("-id")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(Resolutor_detalleList, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['creacion'] = Catalogo.objects.get(nombre="Creacion")
        context['aceptado'] = Catalogo.objects.get(nombre="ACEPTADO")
        context['rechazado'] = Catalogo.objects.get(nombre="RECHAZADO")
        context['resolutor'] = Resolutor.objects.get(pk = pk)
        etapa = Catalogo.objects.get(nombre="DOCUMENTACION")
        requisitos = Resolutor_detalle.objects.filter(resolutor=pk, activo=True, requisito__obligatorio=True, etapa = etapa).order_by("-id")
        completo = True
        for req in requisitos:
            if not req.archivo:
                completo = False
        context['completo'] = completo
        return context
class Resolutor_ejecucion(ListView):
    model = Resolutor_detalle
    template_name = "juridico/resolutor/consultar/resolutor_ejecucion.html"
    context_object_name = "listado_resolutor"

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        ejecucion = Catalogo.objects.get(nombre="EJECUCION")
        queryset = Resolutor_detalle.objects.filter(resolutor=pk, activo=True, requisito__tramite=ejecucion).order_by("-id")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(Resolutor_ejecucion, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['creacion'] = Catalogo.objects.get(nombre="Creacion")
        context['aceptado'] = Catalogo.objects.get(nombre="ACEPTADO")
        context['rechazado'] = Catalogo.objects.get(nombre="RECHAZADO")
        context['resolutor'] = Resolutor.objects.get(pk = pk)
        etapa = Catalogo.objects.get(nombre="DOCUMENTACION")
        requisitos = Resolutor_detalle.objects.filter(resolutor=pk, activo=True, requisito__obligatorio=True, etapa = etapa).order_by("-id")
        completo = True
        for req in requisitos:
            if not req.archivo:
                completo = False
        context['completo'] = completo
        return context
    
""" RESOLUTOR REQUISITOS """
class Resolutor_AltaRequisito(CreateView):
    model = Requisitos
    #fields = ['nombre','obligatorio','formato_default','archivo','tramite'] 
    form_class = Form_Requisito
    template_name = "juridico/resolutor/crear/alta_requisito.html"

    def get_context_data(self, **kwargs):
        context = super(Resolutor_AltaRequisito, self).get_context_data(**kwargs)
        context['id'] = self.kwargs.get('pk')
        return context

    def get_success_url(self):
        messages.success(self.request, 'Hecho')
        return reverse('juridico_app:panel-resolutor')

class Resolutor_ActualizaRequisito(UpdateView):
    model = Requisitos
    #fields = ['nombre','obligatorio','formato_default','archivo','tramite']
    form_class = Form_Requisito
    template_name = "juridico/resolutor/actualizar/requisito.html"


    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        context = super(Resolutor_ActualizaRequisito, self).get_context_data(**kwargs)
        context['id'] = pk
        requisito = Requisitos.objects.get(pk=pk)
        context['requisito'] = requisito if requisito.formato_default else None
        return context

    def get_success_url(self):
        messages.success(self.request, 'Hecho')
        return reverse('juridico_app:panel-resolutor')
        
def Resolutor_EliminaRequisito(request, pk):
    instance = get_object_or_404(Requisitos, pk=pk)
    if request.method == 'POST':
        # Actualiza el registro con los datos enviados en el formulario
        instance.activo = False
        instance.save()
        return HttpResponseRedirect('/')

class resolutor_solicitante(ListAPIView):
    serializer_class = Solicitante_Serialize
    def get_queryset(self):
        kword = self.kwargs['kword']
        queryset = Solicitante.objects.filter(
            Q(rfc__icontains = kword) | Q(nombre__icontains = kword)
        ).order_by('rfc')

        return queryset[:1]
    
class resolutor_solicitanteId(ListAPIView):
    serializer_class = Solicitante_Serialize
    def get_queryset(self):
        kword = self.kwargs['kword']
        queryset = Solicitante.objects.filter(pk=kword)

        return queryset[:1]

class PanelResolutorView(ListView):
    template_name = "juridico/resolutor/consultar/panel_resolutor.html"
    context_object_name = "listado_resolutor"

    def get_queryset(self):
        
        if User.objects.filter(username=self.request.user.username, groups__name__in=['RESOLUTORES ADMINISTRADOR']).exists():
            queryset = Resolutor.objects.order_by("-id").exclude(abogado__isnull=False)
        else:
            user_id = self.request.user.id
            usuarios_instance = User.objects.get(pk=user_id)
            queryset = Resolutor.objects.filter(abogado=usuarios_instance).order_by("-id")

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PanelResolutorView, self).get_context_data(**kwargs)
        usuarios_instance = User.objects.get(pk=self.request.user.id)
        documentacion = Catalogo.objects.get(nombre="DOCUMENTACION")
        firma = Catalogo.objects.get(nombre="FIRMA")
        aceptado = Catalogo.objects.get(nombre="ACEPTADO")
        rechazado = Catalogo.objects.get(nombre="RECHAZADO")
        creacion = Catalogo.objects.get(nombre="Creacion")
        tramite = Catalogo.objects.get(nombre="RESOLUTOR")
        ejecucion = Catalogo.objects.get(nombre="EJECUCION")
        concluido = Catalogo.objects.get(nombre="Concluido")
        #Tab Revision
        revision = Resolutor_detalle.objects.order_by("-resolutor_id").distinct("resolutor_id").exclude(Q(archivo__exact = '')).filter(requisito__obligatorio = True, etapa = documentacion)
        listaRevision = []
        completo = True
        for rev in revision:
            obligado = Resolutor_detalle.objects.filter(resolutor = rev.resolutor, requisito__obligatorio = True)
            for row in obligado:
                if not row.archivo:
                   completo = False
            enFirma = Resolutor_detalle.objects.filter(resolutor = rev.resolutor, etapa=firma)
            if enFirma:   
                completo = False    
            if completo:
                listaRevision.append(row)
            #context['OO'] = "%s %s" % (rev.etapa, firma)
        context['revisar'] = listaRevision        
        #tab firma
        lstFirma = []
        firmados = Resolutor_detalle.objects.filter(etapa = firma, activo=True).order_by("-resolutor_id").distinct("resolutor_id").exclude(Q(resolutor__abogado__isnull=True))
        for row in firmados:
            listDetalle = Resolutor_detalle.objects.filter(resolutor = row.resolutor, etapa=concluido, estatus=concluido)
            if listDetalle:
                lstFirma.extend(listDetalle)
        context['firmar'] = lstFirma
        #tab ejecucion
        context['ejecucion'] = Resolutor_detalle.objects.filter(etapa = documentacion, requisito__tramite=ejecucion, activo=True).order_by("-resolutor_id").distinct("resolutor_id")
        #tab Asignados
        context['asignadosAbogado'] = Resolutor_detalle.objects.filter(etapa = documentacion, estatus__in = (creacion,rechazado), resolutor__abogado=usuarios_instance, activo=True).order_by("-resolutor_id").distinct("resolutor_id")
        #end
        #tab por concluir
        context['concluir'] = Resolutor_detalle.objects.filter(activo=True, etapa=firma).order_by("-id")
        #tab por concluidos
        context['concluidos'] = Resolutor_detalle.objects.filter(activo=True, etapa=concluido, estatus=creacion).order_by("-id")
        context['usuarios_dictiminador'] = User.objects.filter(areas_id = 4, groups__name__contains='Dictaminador')
        context['perfil_usuario'] = "RESOLUTORES" 
        if User.objects.filter(username=self.request.user.username, groups__name__in=['RESOLUTORES ADMINISTRADOR']).exists():
            context['perfil_usuario'] = "RESOLUTORES ADMINISTRADOR"
        elif User.objects.filter(username=self.request.user.username, groups__name__in=['RESOLUTORES DIRECTOR']):
            context['perfil_usuario'] = "RESOLUTORES DIRECTOR"
        elif User.objects.filter(username=self.request.user.username, groups__name__in=['RESOLUTORES EJECUCION']):
            context['perfil_usuario'] = "RESOLUTORES EJECUCION"
        context['tramite'] = tramite
        context['requisitos'] = Requisitos.objects.all().order_by('id')

        return context

def AsignarAbogados(request):
    FormData = request.POST
    resolutor = FormData["resolutor_id"]

    resolutor_instance = Resolutor.objects.get(pk=resolutor)

    if FormData['listado_abogados']:
        user_instance = User.objects.get(pk=FormData['listado_abogados'])
        resolutor_instance.abogado = user_instance
        resolutor_instance.save()
    return JsonResponse({'error': False, 'msj': "Abogado asignado." })

def BuscarAbogadosAsignados(request):
    FormData = request.POST
    
    # Buscamos el resolutor actual
    resolutor_instance = Resolutor.objects.get(id=FormData["resolutor_id"])


    participantes_usuarios = []
    participantes_usuarios_nombre = []
    if resolutor_instance.abogado:
        participantes_usuarios.append(resolutor_instance.abogado.id)
        participantes_usuarios_nombre.append(str(resolutor_instance.abogado.get_full_name()).upper())

    return JsonResponse({'error': False, "abogados_asignados": participantes_usuarios, "abogados_asignados_nombre": participantes_usuarios_nombre, 'msj': "Abogados encontrados." })

class Ver_detalle_resolutor(TemplateView):
    template_name = 'juridico/resolutor/consultar/ver_detalle_resolutor.html'

    def get_context_data(self, **kwargs):
        context = super(Ver_detalle_resolutor, self).get_context_data(**kwargs)
        context['detalle'] = Resolutor_detalle.objects.filter(resolutor_id = self.kwargs.get('pk'))#
        context['detalle_tab'] = Resolutor_detalle.objects.filter(resolutor_id = self.kwargs.get('pk'),activo = True)#

        return context
    
class Elimina_detalle(View):
    
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        instancia = Resolutor_detalle.objects.get(pk=pk)
        instancia.activo = False
        instancia.save()

        return JsonResponse({'res': 'ok'})

def Actualiza_detalle(request):
    pk = request.GET.get('pk')
    FormData = request.POST

    instancia = Resolutor_detalle.objects.get(pk=pk)
    instancia.comentario = FormData["comentario"]
    instancia.estatus = FormData["estatus"]
    instancia.etapa = FormData["estapa"]
    instancia.save()

    return JsonResponse({'result': 'ok'})

def AgregarDetalle(request):
    FormData = request.POST
    usuario = User.objects.get(pk = 114 )
    resolutor = FormData["resolutor_id"]
    resolutor_instance = Resolutor.objects.get(pk=resolutor)
    Resolutor_detalle.objects.create(
                    resolutor=resolutor_instance
                    ,comentarios=FormData['comentarios']
                    ,etapa=FormData['listado_estatus']
                    ,estatus=FormData['listado_etapa']   
                    ,usuario=usuario 
                ).save()

    return JsonResponse({'error': False, 'msj': "Abogados guardados correctamente." })

def Resolutor_Aceptar(request, pk):
    instance = get_object_or_404(Resolutor_detalle, pk=pk)
    # Actualiza el registro con los datos enviados en el formulario
    etapa = Catalogo.objects.get(nombre="ACEPTADO")
    instance.estatus = etapa
    instance.save()

    return JsonResponse({'result': 'Requisito aceptado'})
    
def Resolutor_Rechazar(request, pk):
    FormData = request.POST
    instance = get_object_or_404(Resolutor_detalle, pk=pk)
    # Actualiza el registro con los datos enviados en el formulario
    etapa = Catalogo.objects.get(nombre="RECHAZADO")
    instance.estatus = etapa
    instance.comentarios = FormData['comentarios']
    instance.save()

    return JsonResponse({'result': 'Requisito rechazado'})

def Resolutor_Firma(request, pk):
    instance = get_object_or_404(Resolutor, pk=pk)
    etapa = Catalogo.objects.get(nombre="FIRMA")
    creacion = Catalogo.objects.get(nombre="Creacion")
    if request.user.is_authenticated:
        username = request.user.username
    usuario = User.objects.get(username = username)
    # Actualiza el registro con los datos enviados en el formulario
    Resolutor_detalle.objects.filter(resolutor=instance, activo = True).update(activo = False)
    Resolutor_detalle.objects.create(
        resolutor=instance
        ,comentarios="Se envia para firma"
        ,etapa=etapa
        ,estatus=creacion
        ,usuario=usuario 
    )

    return JsonResponse({'result': 'Enviado para firma'})

def ConcluirManual(request,pk):
    instance = get_object_or_404(Resolutor, pk=pk)
    etapa = Catalogo.objects.get(nombre="Concluido")
    creacion = Catalogo.objects.get(nombre="Creacion")
    if request.user.is_authenticated:
        username = request.user.username
    usuario = User.objects.get(username = username)
    # Actualiza el registro con los datos enviados en el formulario
    Resolutor_detalle.objects.filter(resolutor=instance, activo = True).update(activo = False)
    Resolutor_detalle.objects.create(
        resolutor=instance
        ,comentarios="Concluido manualmente"
        ,etapa=etapa
        ,estatus=creacion
        ,usuario=usuario 
    )

    return JsonResponse({'result': 'Concluido manualmente'})

def generatePdfRefrendo(request,pk):
    # Get the template
    template = get_template('juridico/resolutor/reportes/refrendo.html')
    # Render the template with context
    context = {'data': 'Some data'}
    context = {'resolutor': Resolutor.objects.get(pk=pk)}
    html = template.render(context)
    # Create a PDF file using wkhtmltopdf
    pdf_file = subprocess.run(['wkhtmltopdf', '-', '-'], input=html.encode(), capture_output=True).stdout
    # Create an HTTP response with the PDF file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response

def generatePdfTenencia(request,pk):
    # Get the template
    template = get_template('juridico/resolutor/reportes/tenencia.html')
    # Render the template with context
    context = {'data': 'Some data'}
    context = {'resolutor': Resolutor.objects.get(pk=pk)}
    html = template.render(context)
    # Create a PDF file using wkhtmltopdf
    pdf_file = subprocess.run(['wkhtmltopdf', '-', '-'], input=html.encode(), capture_output=True).stdout
    # Create an HTTP response with the PDF file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response

def generatePdfRefrendoTenencia(request,pk):
    # Get the template
    template = get_template('juridico/resolutor/reportes/refrendoTenencia.html')
    # Render the template with context
    context = {'data': 'Some data'}
    context = {'resolutor': Resolutor.objects.get(pk=pk)}
    html = template.render(context)
    # Create a PDF file using wkhtmltopdf
    pdf_file = subprocess.run(['wkhtmltopdf', '-', '-'], input=html.encode(), capture_output=True).stdout
    # Create an HTTP response with the PDF file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response

def BuscarSolicitante(request):   
    # Buscamos solicitante
    solicitante_instance = Solicitante.objects.get(activo=True)
    return JsonResponse({"solicitante": solicitante_instance.rfc,"id":solicitante_instance.id})
