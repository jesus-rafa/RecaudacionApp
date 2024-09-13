import csv
from datetime import datetime
from applications.users.functions import get_username
from applications.users.mixins import CRUDMixin, GlobalMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)
from django.db.models import Q, Sum, F, Case, Count, When
from django.db.models.fields import IntegerField
from django.db import connection

from .forms import DesarrolloForm, EventoForm, VisitaForm, ProgramaForm, AprobarForm
from .models import (Actividades, Desarrollo, Evento, Formulario, Opciones, Programa_Actualizaciones,
                     Visita, Visita_Detalle, Detalle)
from applications.padrones.models import Programa_Padrones
from applications.users.models import User
from applications.home.models import Codigos_Maestros

# ============================= Actualizaciones ========================================== #

class Programas(GlobalMixin, TemplateView):
    template_name = 'promocion/programas.html'

    def get_context_data(self, **kwargs):
        context = super(Programas, self).get_context_data(**kwargs)

        context['programas'] =  Programa_Actualizaciones.objects.all().exclude(estatus='CANCELADO')
        context['cancelados'] =  Programa_Actualizaciones.objects.filter(estatus='CANCELADO')

        return context


class Actualizaciones(GlobalMixin, ListView):
    template_name = 'promocion/actualizaciones/eventos.html'
    context_object_name = 'desarrollo'

    def get_queryset(self):
        QuerySet = Desarrollo.objects.filter(
            id_evento__id_programa__nombre__in=['MERCADOS','TIANGUIS'], 
            estatus='EN PROCESO'
        ).annotate(
            sum_rfc=Sum(
                Case(
                    When(visita_desarrollo__is_active=True, then=1), default=0, output_field=IntegerField()
                )
            )
        ).order_by('id')

        return QuerySet

class Recorridos(GlobalMixin, ListView):
    template_name = 'promocion/recorridos/eventos.html'
    context_object_name = 'desarrollo'

    def get_queryset(self):
        QuerySet = Desarrollo.objects.filter(
            id_evento__id_programa__nombre='RECORRIDOS', 
            estatus='EN PROCESO'
        ).annotate(
            sum_rfc=Sum(
                Case(
                    When(visita_desarrollo__is_active=True, then=1), default=0, output_field=IntegerField()
                )
            )
        ).order_by('id')

        return QuerySet


class Eventos_Promocion(GlobalMixin, ListView):
    template_name = 'promocion/eventos_promocion.html'
    context_object_name = 'eventos'

    def get_queryset(self):
        QuerySet = Evento.objects.all().annotate(sum_visitas=Count('desarrollo_evento')).order_by('nombre')

        return QuerySet


class Desarrollos(LoginRequiredMixin, ListView):
    template_name = 'promocion/desarrollos.html'
    context_object_name = 'desarrollo'

    def get_queryset(self):
        id_evento = self.kwargs.get('id_evento')

        QuerySet = Desarrollo.objects.filter(
            id_evento = id_evento
        ).annotate(
            sum_rfc=Sum(
                Case(
                    When(visita_desarrollo__is_active=True, then=1), default=0, output_field=IntegerField()
                )
            )
        ).order_by('id')

        return QuerySet



class Admin_Eventos(GlobalMixin, ListView):
    template_name = 'promocion/actualizaciones/admin_eventos.html'
    context_object_name = 'eventos'

    def get_queryset(self):
        id_evento = self.kwargs.get('id')
        return Desarrollo.objects.filter(id=id_evento)

    def get_context_data(self, **kwargs):
        context = super(Admin_Eventos, self).get_context_data(**kwargs)

        idDesarrollo = self.kwargs.get('id')

        context['idDesarrollo'] = idDesarrollo

        context['visitas'] = Visita.objects.contribuyentes_por_desarrollo(
            id_desarrollo=idDesarrollo,
            username=get_username(self)
        )

        return context


class Detalle_Visita(LoginRequiredMixin, ListView):
    template_name = 'promocion/actualizaciones/detalle_visita.html'
    context_object_name = 'visita'

    def get_instance(self):
        id_visita = self.kwargs.get('id')
        return Visita.objects.filter(id=id_visita)

    def get_queryset(self):
        return self.get_instance()

    def get_context_data(self, **kwargs):
        context = super(Detalle_Visita, self).get_context_data(**kwargs)

        id_visita = self.kwargs.get('id')

        instance = self.get_instance()
        context['idBack'] = instance[0].id_desarrollo.id

        context['EstatalCheckForm'] = Formulario.objects.tipo_formulario_1(
            tramite='ESTATAL'
        )
        context['EstatalForm'] = Formulario.objects.tipo_formulario_2(
            tramite='ESTATAL'
        )
        context['FederalCheckForm'] = Formulario.objects.tipo_formulario_1(
            tramite='FEDERAL'
        )
        context['FederalForm'] = Formulario.objects.tipo_formulario_2(
            tramite='FEDERAL'
        )

        context['tramites_federales'] = Visita_Detalle.objects.tramites_por_contribuyente(
            tramite='FEDERAL',
            idVisita=id_visita,
            usuario=get_username(self)
        )
        context['tramites_estatales'] = Visita_Detalle.objects.tramites_por_contribuyente(
            tramite='ESTATAL',
            idVisita=id_visita,
            usuario=get_username(self)
        )

        return context
        

class Ver_Tramites(LoginRequiredMixin, TemplateView):
    template_name = 'promocion/actualizaciones/consulta/ver_tramites.html'

    def get_context_data(self, **kwargs):
        context = super(Ver_Tramites, self).get_context_data(**kwargs)

        id_visita = self.kwargs.get('idVisita')

        context['ver_tramites_federales'] = Visita_Detalle.objects.tramites_por_contribuyente(
            tramite='FEDERAL',
            idVisita=id_visita,
            usuario=''
        ).order_by('folio')

        context['ver_tramites_estatales'] = Visita_Detalle.objects.tramites_por_contribuyente(
            tramite='ESTATAL',
            idVisita=id_visita,
            usuario=''
        ).order_by('folio')

        return context
        

class Todos_Tramites(LoginRequiredMixin, TemplateView):
    template_name = 'promocion/actualizaciones/consulta/todos_tramites.html'

    def get_context_data(self, **kwargs):
        context = super(Todos_Tramites, self).get_context_data(**kwargs)

        rfc = self.kwargs.get('rfc')

        context['tramites_federales'] = Visita_Detalle.objects.tramites_por_contribuyente_todos(
            tramite='FEDERAL',
            rfc=rfc
        ).order_by('folio')

        context['tramites_estatales'] = Visita_Detalle.objects.tramites_por_contribuyente_todos(
            tramite='ESTATAL',
            rfc=rfc
        ).order_by('folio')

        return context


class Alta_Programa(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Programa_Actualizaciones
    template_name = 'promocion/programas/alta_programa.html'
    form_class = ProgramaForm
    success_message = 'Programa Creado exitosamente!'

    def form_valid(self, form):
        form.instance.estatus = 'NUEVO'
        form.instance.usuario = get_username(self)

        return super(Alta_Programa, self).form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Alta_Evento(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Evento
    template_name = 'promocion/eventos/alta_evento.html'
    form_class = EventoForm
    success_message = 'Evento Creado exitosamente!'

    def form_valid(self, form):
        form.instance.tipo = 'EN PROCESO'
        #form.instance.usuario = get_username(self)

        return super(Alta_Evento, self).form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

class Alta_Desarrollo(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Desarrollo
    template_name = 'promocion/desarrollos/alta_desarrollo.html'
    form_class = DesarrolloForm
    success_message = 'Recorrido Creado exitosamente!'

    def form_valid(self, form):
        #form.instance.estatus = 'NUEVO'
        #form.instance.usuario = get_username(self)

        return super(Alta_Desarrollo, self).form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Editar_Programa(LoginRequiredMixin, SuccessMessageMixin, UpdateView):    
    model = Programa_Actualizaciones
    template_name = 'promocion/programas/editar_programa.html'
    form_class = ProgramaForm
    success_message = 'Programa actualizado exitosamente!'

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Ver_Programa(LoginRequiredMixin, TemplateView):
    template_name = 'promocion/programas/ver_programa.html'

    def get_context_data(self, **kwargs):
        context = super(Ver_Programa, self).get_context_data(**kwargs)

        id_programa = self.kwargs.get('pk')

        context['detalle'] = Detalle.objects.filter(
            programa=id_programa
        ).order_by('fecha')

        return context


class Aprobar_Programa(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'promocion/programas/aprobar.html'
    success_message = 'Actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Aprobar_Programa, self).get_context_data(**kwargs)
        
        context['id_programa'] = self.kwargs['pk']

        context['form'] = AprobarForm    
        
        return context

    def post(self, request, *args, **kwargs):
        id_programa = self.kwargs['pk']
        
        instance = Programa_Actualizaciones.objects.get(id = str(id_programa))
        instance.estatus = request.POST['estatus']
        instance.save()

        Detalle.objects.create(
            programa=instance,
            fecha=datetime.date.today(),
            comentarios=request.POST['comentarios'],
            estatus=request.POST['estatus'],
            usuario=get_username(self)
        )

        return redirect(self.request.META['HTTP_REFERER'])

        
class Alta_Visita(CRUDMixin, SuccessMessageMixin, CreateView):
    permission_required = ('add_visita')
    model = Visita
    template_name = 'promocion/actualizaciones/crear/alta_visita.html'
    form_class = VisitaForm
    success_message = 'Contribuyente Creado exitosamente!'

    def get_form_kwargs(self):
        kwargs = super(Alta_Visita, self).get_form_kwargs()

        kwargs['pk'] = self.kwargs.get('id')

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Alta_Visita, self).get_context_data(**kwargs)

        context['idDesarrollo'] = self.kwargs.get('id')

        return context

    def form_valid(self, form):
        form.instance.id_evento = form.cleaned_data['id_desarrollo'].id
        form.instance.rfc = form.cleaned_data['rfc'].upper().strip()
        form.instance.nombre = form.cleaned_data['nombre'].upper().strip()
        form.instance.usuario = get_username(self)

        return super(Alta_Visita, self).form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Editar_Visita(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_visita')
    model = Visita
    template_name = 'promocion/actualizaciones/editar/editar_visita.html'
    form_class = VisitaForm
    success_message = 'Contribuyente actualizado exitosamente!'

    def get_form_kwargs(self):
        kwargs = super(Editar_Visita, self).get_form_kwargs()

        kwargs['pk'] = self.kwargs.get('idDesarrollo')

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Editar_Visita, self).get_context_data(**kwargs)

        context['idDesarrollo'] = self.kwargs.get('idDesarrollo')

        return context

    def form_valid(self, form):
        form.instance.id_evento = form.cleaned_data['id_desarrollo'].id
        form.instance.rfc = form.cleaned_data['rfc'].upper().strip()
        form.instance.nombre = form.cleaned_data['nombre'].upper().strip()
        form.instance.usuario = get_username(self)

        return super(Editar_Visita, self).form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Eliminar_Visita(CRUDMixin, DeleteView):
    permission_required = ('delete_visita')

    model = Visita
    template_name = ''

    def delete(self, request, *args, **kwargs):
        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            obj_archivo = self.get_object()
            obj_archivo.is_active = False
            obj_archivo.save()

            message = 'Contribuyente Eliminado!'
            response = JsonResponse({'message': message})
            return response
        else:
            return self.request.META['HTTP_REFERER']

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Alta_Detalle(LoginRequiredMixin, TemplateView):
    template_name = 'promocion/actualizaciones/crear/alta_detalle.html'

    def get_context_data(self, **kwargs):
        context = super(Alta_Detalle, self).get_context_data(**kwargs)

        id_visita = self.kwargs.get('idVisita')
        id_actividad = self.kwargs.get('idActividad')

        context['idActividad'] = id_actividad
        context['idVisita'] = id_visita
        context['actividad'] = Actividades.objects.filter(
            id=id_actividad
        )
        context['TransactForm'] = Formulario.objects.get_formulario(
            idActividad=id_actividad
        )
        context['opcion'] = Opciones.objects.all().order_by('valor')

        return context

    def post(self, request, *args, **kwargs):

        id_visita = self.kwargs.get('idVisita')
        id_actividad = self.kwargs.get('idActividad')

        def get_folio():
            try:
                last_folio = Visita_Detalle.objects.latest('folio')
                folio = int(str(last_folio)) + 1
            except:
                folio = 1

            return folio

        if request.method == 'POST':
            FormData = request.POST

            obj1 = Visita.objects.filter(id=id_visita)
            obj2 = Actividades.objects.filter(id=id_actividad)
            folio = get_folio()

            if Visita_Detalle.objects.filter(id_visita=id_visita, id_actividad=id_actividad).exists():
                CurrentData = Visita_Detalle.objects.filter(
                    id_visita=id_visita,
                    id_actividad=id_actividad
                )

                flag = False
                insert = True
                datos_actuales = []
                datos_nuevos = []
                # Validacion no permitir repetir periodos en el mismo ejercicio.
                for key, value in FormData.items():
                    for row in CurrentData:
                        if key == 'ejercicio' and row.dato == 'ejercicio':
                            if value == row.valor:
                                flag = True
                        if key == 'periodo' and row.dato == 'periodo':
                            datos_actuales = row.valor.split(',')
                            datos_nuevos = value.split(',')

                if flag:
                    for dato in datos_nuevos:
                        if dato in datos_actuales:
                            insert = False

                    if insert:
                        for key, value in FormData.items():
                            if key != 'csrfmiddlewaretoken':
                                Visita_Detalle.objects.create(
                                    folio=folio,
                                    id_visita=obj1[0],
                                    id_actividad=obj2[0],
                                    dato=key,
                                    valor=value,
                                    usuario = get_username(self)
                                )

                        messages.success(self.request, 'Tramites Guardados')
                    else:
                        mensaje = "Ya estan registrados estos periodos: " + \
                            (',').join(datos_actuales)
                        messages.error(self.request, mensaje)

                else:
                    for key, value in FormData.items():
                        if key != 'csrfmiddlewaretoken':
                            Visita_Detalle.objects.create(
                                folio=folio,
                                id_visita=obj1[0],
                                id_actividad=obj2[0],
                                dato=key,
                                valor=value,
                                usuario = get_username(self)
                            )

                    messages.success(self.request, 'Tramites Guardados')
            else:
                for key, value in FormData.items():
                    if key != 'csrfmiddlewaretoken':
                        Visita_Detalle.objects.create(
                            folio=folio,
                            id_visita=obj1[0],
                            id_actividad=obj2[0],
                            dato=key,
                            valor=value,
                            usuario = get_username(self)
                        )

                messages.success(self.request, 'Tramites Guardados')

        return redirect(self.request.META['HTTP_REFERER'])


class Guardar_Detalle(LoginRequiredMixin, TemplateView):
    template_name = ''
    #success_message = 'Tramites guardados!'

    def post(self, request, *args, **kwargs):

        id_visita = self.kwargs.get('idVisita')

        def get_folio():
            try:
                last_folio = Visita_Detalle.objects.latest('folio')
                folio = int(str(last_folio)) + 1
            except:
                folio = 1

            return folio

        if request.method == 'POST':
            FormData = request.POST

            obj1 = Visita.objects.filter(id=id_visita)
            obj2 = []
            detalle = []

            # borrar las actividades desmarcadas
            actividades = Visita_Detalle.objects.filter(
                id_visita=obj1[0],
                valor='on',
                usuario=get_username(self)
            )
            for row in actividades:
                if not row.dato in FormData:
                    row.delete()

            for key, value in FormData.items():
                if key != 'csrfmiddlewaretoken':
                    obj2 = Formulario.objects.filter(campo=key)

                    detalle = Visita_Detalle.objects.filter(
                        id_visita=obj1[0],
                        id_actividad=obj2[0].id_actividad,
                    )

                    if not detalle:
                        Visita_Detalle.objects.create(
                            folio=get_folio(),
                            id_visita=obj1[0],
                            id_actividad=obj2[0].id_actividad,
                            dato=key,
                            valor=value,
                            usuario = get_username(self)
                        )

                    obj2 = []
                    detalle = []

            messages.success(self.request, 'Guardado Correctamente')

        return redirect(self.request.META['HTTP_REFERER'])


class Editar_Detalle(LoginRequiredMixin, TemplateView):
    template_name = 'promocion/actualizaciones/editar/editar_detalle.html'

    def get_instance(self):
        folio = self.kwargs.get('folio')
        queryset = Visita_Detalle.objects.get_visita_detalle(
            folio=folio
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Editar_Detalle, self).get_context_data(**kwargs)

        id_actividad = self.kwargs.get('idActividad')

        context['idActividad'] = id_actividad
        context['actividad'] = Actividades.objects.filter(
            id=id_actividad
        )
        context['TransactForm'] = Formulario.objects.get_formulario(
            idActividad=id_actividad
        )

        context['FormEdit'] = self.get_instance()

        context['opcion'] = Opciones.objects.all().order_by('valor')

        return context

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            FormData = request.POST

            instance = self.get_instance()

            for campo in instance:
                obj = Visita_Detalle.objects.get(id=campo.id)

                for key, value in FormData.items():
                    if obj.dato == key:
                        obj.valor = value
                        obj.save()

            messages.success(self.request, 'Tramites Actualizados')

        return redirect(self.request.META['HTTP_REFERER'])


class Eliminar_Detalle(LoginRequiredMixin, DeleteView):
    template_name = ''

    def get_instance(self):
        folio = self.kwargs.get('folio')
        queryset = Visita_Detalle.objects.get_visita_detalle(
            folio=folio
        )
        return queryset

    def delete(self, request, *args, **kwargs):
        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            obj = self.get_instance()
            obj.delete()

            response = JsonResponse({'message': 'Tramite Eliminado!'})
            messages.success(self.request, 'Tramites Eliminado')
            return response
        else:
            return self.request.META['HTTP_REFERER']
            

class Validar_RFC(ListView):
    model = Visita
    template_name = ''

    def get_queryset(self):
        idDesarrollo = self.kwargs.get('idDesarrollo')
        rfc = self.kwargs.get('rfc')

        if Visita.objects.filter(id_desarrollo=idDesarrollo, rfc__icontains=rfc, is_active=True).exists():
            queryset = True
        else:
            queryset = False

        return queryset

    def get(self, request, *args, **kwargs):
        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            flag = self.get_queryset()

            return JsonResponse({'data': flag})


# ============================= Convenios ========================================== #


class Convenios(GlobalMixin, ListView):
    template_name = 'promocion/convenios.html'
    context_object_name = 'convenios'

    def get_queryset(self):
        QuerySet = None
        return QuerySet


class Ver_Mercado(LoginRequiredMixin, TemplateView):
    template_name = 'promocion/actualizaciones/consulta/ver_detalle.html'

    def get_context_data(self, **kwargs):
        context = super(Ver_Mercado, self).get_context_data(**kwargs)

        id_mercado = str(self.kwargs.get('id_mercado'))

        cursor = connection.cursor()
        mySql = f"""SELECT 
                    c.id_desarrollo_id as id,
                    b.actividad as actividad_,
                    b.tipo_tramite as tipo_tramite_,
                    CASE 
                        WHEN b.actividad = 'CFDI' OR b.actividad = 'DECLARACIONES FEDERALES' OR b.actividad = 'DECLARACIONES ESTATALES' OR b.actividad = 'RESICO'
                            THEN 
                                SUM(CASE WHEN a.dato = 'periodo' 
                                    THEN
                                        ((LENGTH(a.valor) - LENGTH(replace(a.valor, ',', ''))) / LENGTH(',')) + 1
                                    ELSE 0
                                END)
                            ELSE 
                                COUNT(DISTINCT a.folio) 
                    END AS total_
                FROM public.promocion_visita_detalle AS a
                    INNER JOIN promocion_actividades b
                        on b.id = a.id_actividad_id
                    INNER JOIN promocion_visita c
                        on c.id = a.id_visita_id
                    WHERE c.id_desarrollo_id = {id_mercado}
                        AND c.is_active = true
                    GROUP BY 
                        c.id_desarrollo_id,
                        B.tipo_tramite,
                        B.actividad
                    ORDER BY c.id_desarrollo_id, B.actividad;"""

        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
            
        context['detalle'] = result

        total = 0
        for row in result:
            total = total + int(row['total_'])

        context['total_tramites'] = total

        return context


class Lista_Promocion(GlobalMixin, ListView):
    template_name = 'promocion/lista_programacion.html'
    model = Programa_Padrones
    context_object_name = 'programacion'

    def get_context_data(self, **kwargs):
        context = super(Lista_Promocion, self).get_context_data(**kwargs)

        context['filter_seguimiento'] = User.objects.filter(groups__name__contains='JEFE CALIDAD')

        #context['filter_etapa'] = Codigos_Maestros.objects.filter(codigo='XXSTAGE_PADRONES').order_by('id') 

        #context['filter_estatus'] = Codigos_Maestros.objects.filter(codigo='XXSTATUS_PADRONES').order_by('id')

        context['filter_programa'] = Programa_Padrones.objects.filter(
            ~Q(estatus='CONCLUIDO'),
            area = 'PROMOCION'
        ).order_by('programa').values('programa').distinct()

        #context['filter_area'] = Programa_Padrones.objects.order_by('area').values('area').distinct()

        return context
    
    def get_queryset(self):
        
        queryset = Programa_Padrones.objects.filtrar(
            kword=self.request.GET.get("kword", ''),
            user=self.request.GET.get("user", ''),
            etapa=self.request.GET.get("etapa", ''),
            status=self.request.GET.get("estatus", ''),
            program=self.request.GET.get("program", ''),
            area='PROMOCION',
            top=self.request.GET.get("top", ''),
        )
        
        return queryset
