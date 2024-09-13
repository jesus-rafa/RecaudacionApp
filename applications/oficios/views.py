import datetime
import json

from applications.home.models import Codigos_Maestros
from applications.users.mixins import GlobalMixin
from applications.users.models import Areas, User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import connection
from django.db.models import CharField, F, Q, Value
from django.http.response import JsonResponse
from django.shortcuts import HttpResponse, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, ListView, TemplateView,
                                  UpdateView, View)
from django.views.generic.detail import DetailView

from .forms import (CerrarForm, CerrarRecibidoForm, CompartidosForm,
                    NuevoOficioForm, OficiosForm, PermisosForm, RecibidosForm,
                    RecibirOficioForm, TurnarForm)
from .models import (CC, CCO, Archivos_Oficios, Archivos_Recibidos,
                     Compartidos, Oficios, Permisos, Recibidos)


class CorrespondenciaView(GlobalMixin, ListView):
    template_name = 'oficios/correspondencia.html'
    context_object_name = 'oficios_on'

    def get_queryset(self):
        user = self.request.user.username
        obj = Permisos.objects.filter(usuario__contains=user).values_list(
            'permisos__username', flat=True)

        permission_list = list(obj)
        permission_list.append(user)

        return Oficios.objects.filter(usuario__in=permission_list, estatus='EN PROCESO').union(Oficios.objects.filter(enviado__contains=user, estatus='EN PROCESO'))

    def get_context_data(self, **kwargs):
        context = super(CorrespondenciaView, self).get_context_data(**kwargs)
        url_patameter = self.kwargs.get('item')

        if url_patameter == '1':
            # Retornar el ultimo folio creado
            if self.request.user.area == '205':
                folio_len = 15  # numero de caracteres del folio de administracion
            elif self.request.user.area == 'EJECUCION':
                folio_len = 25  # numero de caracteres del folio de ejecución
            else:
                folio_len = 24  # numero de caracteres del folio de recaudacion

            cursor = connection.cursor()
            sql = f'''select folio from public.oficios_oficios
	                    where length(folio) = {folio_len}
	                  order by id DESC
	                  limit 1'''
            cursor.execute(sql)
            fieldnames = [name[0] for name in cursor.description]
            result = []
            for row in cursor.fetchall():
                rowset = []
                for field in zip(fieldnames, row):
                    rowset.append(field)
                result.append(dict(rowset))

            context['msg'] = result[0]['folio']
        else:
            context['msg'] = ''

        user = self.request.user.username
        obj = Permisos.objects.filter(usuario__contains=user).values_list(
            'permisos__username', flat=True)

        permission_list = list(obj)
        permission_list.append(user)

        context['oficios_off'] = Oficios.objects.filter(usuario__in=permission_list, estatus__in=['CONCLUIDO', 'CANCELADO']).union(
            Oficios.objects.filter(enviado__contains=user, estatus__in=['CONCLUIDO', 'CANCELADO']))
        context['recibidos_on'] = Recibidos.objects.filter(usuario__in=permission_list, estatus='EN PROCESO').union(
            Recibidos.objects.filter(para__contains=user, estatus='EN PROCESO'))
        context['recibidos_off'] = Recibidos.objects.filter(usuario__in=permission_list, estatus='CONCLUIDO').union(
            Recibidos.objects.filter(para__contains=user, estatus='CONCLUIDO'))

        context['permisos'] = Permisos.objects.filter(usuario__contains=user)
        context['compartidos'] = Compartidos.objects.filter(
            usuario__contains=user)

        return context


class Correspondencia(LoginRequiredMixin, TemplateView):
    template_name = 'oficios/correspondencia/panel.html'

    def get_context_data(self, **kwargs):
        context = super(Correspondencia, self).get_context_data(**kwargs)
        url_patameter = self.kwargs.get('item')

        #se agrego recientemente
        mostrar_individual = self.kwargs.get('vista')  
        context['mostrar_ind'] = mostrar_individual
        user = self.request.user.username

        context['id_personal'] = User.objects.all()

        usuario_esp = self.request.user.username
        if User.objects.filter(username=usuario_esp, groups__name__contains='CORRESPONDENCIA ESPECIFICO'):
            context['permission'] = 'CORRESPONDENCIA ESPECIFICO'
        #se agrego recientemente 

        if url_patameter == '1':
            # Retornar el ultimo folio creado
            if self.request.user.area == '205':
                folio_len = 15  # numero de caracteres del folio de administracion
            elif self.request.user.area == 'EJECUCION':
                folio_len = 25  # numero de caracteres del folio de ejecución
            else:
                folio_len = 24  # numero de caracteres del folio de recaudacion

            cursor = connection.cursor()
            sql = f'''select folio from public.oficios_oficios
	                    where length(folio) = {folio_len}
	                  order by id DESC
	                  limit 1'''
            cursor.execute(sql)
            fieldnames = [name[0] for name in cursor.description]
            result = []
            for row in cursor.fetchall():
                rowset = []
                for field in zip(fieldnames, row):
                    rowset.append(field)
                result.append(dict(rowset))

            context['msg'] = result[0]['folio']
        else:
            context['msg'] = ''

        context['hoy'] = datetime.date.today()

        # USUARIOS
        # usuarios recaudacion
        lista_recaudacion = User.objects.filter(~Q(area='EJECUCION'), is_active=True, is_superuser=False).values_list('username', flat=True)
        # usuarios recaudacion
        lista_ejecucion = User.objects.filter(area='EJECUCION', is_active=True, is_superuser=False).values_list('username', flat=True)
        
        # OFICIOS
        # Agregar oficios que no se han visto y fueron copiados
        copia_oficios = CC.objects.filter(
            user=self.request.user.id,
            visto=False
        )
        lista_oficios = []
        for row in copia_oficios:
            lista_oficios.append(str(row.oficio.id))

        if User.objects.filter(username=user, groups__name__in=['DIRECTOR', 'ASISTENTE ADMINISTRATIVO']).exists():
            context['oficios'] = Oficios.objects.filter(
                estatus='EN PROCESO',
                usuario__in=lista_recaudacion
            )

        elif User.objects.filter(username=user, groups__name__in=['COORDINADORA DE EJECUCIÓN', 'SECRETARIO']).exists():
            context['oficios'] = Oficios.objects.filter(
                estatus='EN PROCESO',
                usuario__in=lista_ejecucion
            )

        else:
            context['oficios'] = Oficios.objects.filter(
                estatus='EN PROCESO',
                usuario=user
            ).union(
                Oficios.objects.filter(
                    id__in=lista_oficios
                ).exclude(
                    pdf=''
                )
            )

        # Mostar oficios con copia
        copia_oficios_concluidos = CC.objects.filter(
            user=self.request.user.id
        )
        lista_oficios_concluidos = []
        for row in copia_oficios_concluidos:
            lista_oficios_concluidos.append(str(row.oficio.id))

        if User.objects.filter(username=user, groups__name__in=['DIRECTOR', 'ASISTENTE ADMINISTRATIVO']).exists():
            context['oficios_concluidos'] = Oficios.objects.filter(
                ~Q(estatus='EN PROCESO'),
                usuario__in=lista_recaudacion
            )

        elif User.objects.filter(username=user, groups__name__in=['COORDINADORA DE EJECUCIÓN', 'SECRETARIO']).exists():
            context['oficios_concluidos'] = Oficios.objects.filter(
                ~Q(estatus='EN PROCESO'),
                usuario__in=lista_ejecucion
            )

        else:
            context['oficios_concluidos'] = Oficios.objects.filter(
                usuario=user
            ).exclude(
                estatus='EN PROCESO'
            ).union(
                Oficios.objects.filter(
                    id__in=lista_oficios_concluidos
                ).exclude(
                    estatus='EN PROCESO'
                )
            )

        # RECIBIDOS
        # Agregar oficios que no se han visto y fueron copiados
        copia_recibidos = CCO.objects.filter(
            user=self.request.user.id,
            visto=False,
            tipo='C'
        )
        lista_recibidos = []
        for row in copia_recibidos:
            lista_recibidos.append(str(row.oficio))

        # Agregar oficios que no se han visto y fueron turnados
        turnados_recibidos = CCO.objects.filter(
            user=self.request.user.id,
            respuesta=False,
            tipo='T'
        )
        lista_turnados_recibidos = []
        for row in turnados_recibidos:
            lista_turnados_recibidos.append(str(row.oficio))

        # Mostrar estatus TURNADO si fue turnado por el usurio
        # if CCO.objects.filter(enviado_por = user, tipo='T').exists():
        #     context['turnado'] = 1
        # else:
        #     context['turnado'] = 0

        for element in lista_recibidos:
            if element in lista_turnados_recibidos:
                lista_recibidos.remove(element)

        if User.objects.filter(username=user, groups__name__in=['ASISTENTE ADMINISTRATIVO']).exists():
            # context['recibidos'] = Recibidos.objects.filter(
            #     estatus__in = ['EN PROCESO','RECHAZADO'],
            #     unidad=self.request.user.unidad.id
            # )

            context['recibidos'] = Recibidos.objects.recibidos(
                username=user,
                copias=lista_recibidos,
                turnados=lista_turnados_recibidos,
                para=mostrar_individual, #agregardo
                user_login= self.request.user.username #agregardo
            )
        
        elif User.objects.filter(username=user, groups__name__in=['COORDINADORA DE EJECUCIÓN', 'SECRETARIO']).exists():
            if mostrar_individual == 0:#agregardo
                context['recibidos'] = Recibidos.objects.filter(
                    ~Q(estatus='CONCLUIDO'),
                    usuario__in=lista_ejecucion
                )
            else:#agregardo
                context['recibidos'] = Recibidos.objects.filter(
                    ~Q(estatus='CONCLUIDO'),
                    usuario__in=lista_ejecucion,
                    para=self.request.user.username
                )

        else:

            context['recibidos'] = Recibidos.objects.recibidos(
                username=user,
                copias=lista_recibidos,
                turnados=lista_turnados_recibidos,
                para=mostrar_individual,#agregardo
                user_login= self.request.user.username#agregardo
            )

        # RECIBIDOS - TODO LO DEMAS
        # Agregar oficios vistos y fueron copiados
        copia_recibidos_concluidos = CCO.objects.filter(
            user=self.request.user.id,
            visto=True
        )
        lista_recibidos_concluidos = []
        for row in copia_recibidos_concluidos:
            lista_recibidos_concluidos.append(str(row.oficio))

        if User.objects.filter(username=user, groups__name__in=['DIRECTOR', 'ASISTENTE ADMINISTRATIVO']).exists():
            context['recibidos_concluidos'] = Recibidos.objects.filter(
                ~Q(estatus='EN PROCESO'),
                unidad=self.request.user.unidad.id
            )

        elif User.objects.filter(username=user, groups__name__in=['COORDINADORA DE EJECUCIÓN', 'SECRETARIO']).exists():
            context['recibidos_concluidos'] = Recibidos.objects.filter(
                estatus='CONCLUIDO',
                usuario__in=lista_ejecucion
            )

        else:
            context['recibidos_concluidos'] = Recibidos.objects.recibidos_concluidos(
                username=user,
                copias=lista_recibidos_concluidos
            )

        return context


class Control_Oficios(GlobalMixin, ListView):
    template_name = 'oficios/control_oficios.html'
    model = Permisos
    context_object_name = 'permisos'

    def get_queryset(self):
        username = self.request.user.username
        return Permisos.objects.filter(usuario__contains=username)


class Lista_Oficios(GlobalMixin, ListView):
    template_name = 'oficios/lista_oficios.html'
    model = Oficios
    context_object_name = 'oficios'

    def get_queryset(self):
        user = self.request.user.username

        obj = Permisos.objects.filter(usuario__contains=user).values_list(
            'permisos__username', flat=True)

        # print(Permisos.objects.filter(usuario=user).values_list('permisos'))

        # print(Permisos.objects.filter(usuario=user).values('usuario__username'))

        # for obj in Permisos.objects.filter(permisos=user):
        #     print(obj)
        #obj = Permisos.objects.annotate(arr=ArrayAgg('usuario')).values_list('permisos')

        #permission_list = ['root', 'mmedallom']
        permission_list = list(obj)
        permission_list.append(user)

        print(permission_list)

        return Oficios.objects.filter(usuario__in=permission_list)
        # return Oficios.objects.mostrar_oficios(permission_list)

    # def get_object(self, **kwwargs):

    #     return

    def get_context_data(self, **kwargs):
        context = super(Lista_Oficios, self).get_context_data(**kwargs)
        url_patameter = self.kwargs.get('item')

        if url_patameter == '1':
            context['msg'] = Oficios.objects.latest('id')
        else:
            context['msg'] = ''

        return context


class Lista_Recibidos(GlobalMixin, ListView):
    template_name = 'oficios/lista_recibidos.html'
    model = Recibidos
    context_object_name = 'oficios'

    def get_queryset(self):
        user = self.request.user.username
        obj = Permisos.objects.filter(usuario=user).values_list(
            'permisos__username', flat=True)

        permission_list = list(obj)
        permission_list.append(user)

        return Recibidos.objects.mostrar_recibidos(permission_list)


class Alta_Oficios(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Oficios
    template_name = 'oficios/alta_oficios.html'
    form_class = OficiosForm

    def get_context_data(self, **kwargs):
        context = super(Alta_Oficios, self).get_context_data(**kwargs)
        context['usuarios'] = User.objects.filter(is_superuser=False)
        return context

    def form_valid(self, form):
        send_by = form.cleaned_data['enviado']
        start = str(send_by).find('(') + 1
        end = str(send_by).find(')')

        def get_folio():

            if self.request.user.area == '205':
                folio_len = 15  # numero de caracteres del folio de administracion
            elif self.request.user.area == 'EJECUCION':
                folio_len = 25  # numero de caracteres del folio de ejecución
            else:
                folio_len = 24  # numero de caracteres del folio de recaudacion

            # Retornar el ultimo folio creado
            cursor = connection.cursor()
            sql = f'''select folio from public.oficios_oficios
	                    where length(folio) = {folio_len}
	                  order by id DESC
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

            year = datetime.date.today().year

            if self.request.user.area == '205':
                if query != []:
                    query_id = str(query[0]['folio'])[6:10]
                    query_year = str(query[0]['folio'])[11:]

                    if year == int(query_year):
                        new_id = int(query_id) + 1
                    else:
                        new_id = 1

                    folio = 'SATEG-' + str(new_id).zfill(4) + '/' + str(year)

                else:
                    folio = 'SATEG-0001/' + str(year)
            elif self.request.user.area == 'EJECUCION':
                if query != []:
                    query_id = str(query[0]['folio'])[15:20]
                    query_year = str(query[0]['folio'])[21:]
                    if year == int(query_year):
                        new_id = int(query_id) + 1
                    else:
                        new_id = 1
                else:
                    new_id = 1
                folio = 'SATEG-03-03-00-' + \
                    str(new_id).zfill(5) + '/' + str(year)
            else:
                query_id = str(query[0]['folio'])[15:19]
                query_year = str(query[0]['folio'])[20:]

                if year == int(query_year):
                    new_id = int(query_id) + 1
                else:
                    new_id = 1

                folio = 'SATEG-03-02-00-' + \
                    str(new_id).zfill(4) + '/' + str(year)

            return folio

        form.instance.usuario = self.request.user.username
        form.instance.estatus = 'EN PROCESO'
        form.instance.folio = get_folio()
        form.instance.enviado = str(send_by)[start:end]

        return super(Alta_Oficios, self).form_valid(form)

    def get_initial(self):
        return {
            "folio": '0',
            "enviado": self.request.user.nombres + ' ' + self.request.user.apellidos
        }

    def get_success_url(self):
        return reverse_lazy('oficios_app:correspondencia', args=(1,))


class Cerrar_Oficio(LoginRequiredMixin, TemplateView):
    template_name = 'oficios/cerrar_oficio.html'
    success_message = 'Cerrado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Cerrar_Oficio, self).get_context_data(**kwargs)
        context['id_oficio'] = self.kwargs['pk']

        context['form'] = CerrarForm

        return context

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']

        instance = Oficios.objects.get(id=str(id))
        instance.estatus = request.POST['estatus']
        instance.comentarios = request.POST['comentarios']
        instance.save()

        messages.success(self.request, 'oficio')

        return redirect(reverse('oficios_app:panel', kwargs={"item": 0}))


class Cerrar_Oficio_Recibido(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'oficios/cerrar_oficio_recibido.html'
    success_message = 'Cerrado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Cerrar_Oficio_Recibido,
                        self).get_context_data(**kwargs)
        context['id_oficio'] = self.kwargs['pk']

        context['form'] = CerrarRecibidoForm

        return context

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']

        filepath = request.FILES['pdf_respuesta'] if 'pdf_respuesta' in request.FILES else False
        if filepath != False:
            pdf_respuesta = request.FILES['pdf_respuesta']
        else:
            pdf_respuesta = ''

        instance = Recibidos.objects.get(id=str(id))
        instance.fecha_respuesta = datetime.date.today()
        instance.estatus = request.POST['estatus']
        instance.comentarios = request.POST['comentarios']
        instance.pdf_respuesta = pdf_respuesta
        instance.save()

        messages.success(self.request, 'recibido')

        return redirect(self.request.META['HTTP_REFERER'])

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Contestar_Oficio_Recibido(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'oficios/contestar_oficio_recibido.html'
    success_message = 'Cerrado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Contestar_Oficio_Recibido,
                        self).get_context_data(**kwargs)
        context['id_oficio'] = self.kwargs['pk']

        context['form'] = CerrarRecibidoForm

        return context

    def post(self, request, *args, **kwargs):

        filepath = request.FILES['pdf_respuesta'] if 'pdf_respuesta' in request.FILES else False
        if filepath != False:
            pdf_respuesta = request.FILES['pdf_respuesta']
        else:
            pdf_respuesta = ''

        instance = CCO.objects.get(
            oficio=self.kwargs['pk'],
            user=self.request.user.id,
            tipo='T',
            estatus='EN PROCESO'
        )

        instance.declinado = False
        instance.visto = True
        instance.respuesta = True
        instance.fecha_respuesta = datetime.datetime.today()
        instance.estatus = request.POST['estatus']
        instance.comentarios = request.POST['comentarios']
        instance.archivo = pdf_respuesta
        instance.save()

        messages.success(self.request, 'recibido')

        return redirect(self.request.META['HTTP_REFERER'])

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Cerrar_Recibido(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'oficios/cerrar_recibido.html'
    success_message = 'Cerrado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Cerrar_Recibido, self).get_context_data(**kwargs)
        context['id_oficio'] = self.kwargs['pk']

        context['form'] = CerrarForm

        return context

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']

        instance = Recibidos.objects.get(id=str(id))
        instance.estatus = request.POST['estatus']
        instance.comentarios = request.POST['comentarios']
        instance.save()

        messages.error(self.request, 'recibido')

        return redirect(self.request.META['HTTP_REFERER'])

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Alta_Recibidos(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Recibidos
    template_name = 'oficios/alta_recibidos.html'
    form_class = RecibidosForm
    success_message = 'Folio creado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Alta_Recibidos, self).get_context_data(**kwargs)

        context['usuarios'] = User.objects.filter(is_superuser=False)
        context['area'] = Codigos_Maestros.objects.filter(codigo='XXAREA')
        context['para'] = User.objects.filter(is_superuser=False)
        context['todos'] = User.objects.filter(is_superuser=False)

        return context

    def form_valid(self, form):
        user = self.request.user.username

        send_to = form.cleaned_data['para']
        area = form.cleaned_data['area']

        obj = User.objects.filter(id=str(send_to))
        obj2 = Codigos_Maestros.objects.filter(id=str(area))

        if form.instance.pdf:
            form.instance.estatus = 'CONCLUIDO'
        else:
            form.instance.estatus = 'EN PROCESO'

        form.instance.usuario = user
        form.instance.para = obj[0].username
        form.instance.area = obj2[0].comentario

        return super(Alta_Recibidos, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('oficios_app:correspondencia', args=(0,))


class Nuevo_Oficio(LoginRequiredMixin, TemplateView):
    template_name = 'oficios/nuevo_oficio.html'

    def get_context_data(self, **kwargs):
        context = super(Nuevo_Oficio, self).get_context_data(**kwargs)

        context['usuarios'] = User.objects.filter(
            is_superuser=False, is_active=True)
        context['form'] = NuevoOficioForm

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user.username

        # send_by = request.POST['enviado']
        # start = str(send_by).find('(') + 1
        # end = str(send_by).find(')')

        def get_folio():

            if self.request.user.area == '205':
                folio_len = 15  # numero de caracteres del folio de administracion
            elif self.request.user.area == 'EJECUCION':
                folio_len = 25 # número de caracteres del folio de ejecucción
            else:
                folio_len = 24  # numero de caracteres del folio de recaudacion

            # Retornar el ultimo folio creado
            cursor = connection.cursor()
            sql = f'''select folio from public.oficios_oficios
	                    where length(folio) = {folio_len}
	                  order by id DESC
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

            year = datetime.date.today().year

            if self.request.user.area == '205':
                if query != []:
                    query_id = str(query[0]['folio'])[6:10]
                    query_year = str(query[0]['folio'])[11:]

                    if year == int(query_year):
                        new_id = int(query_id) + 1
                    else:
                        new_id = 1

                    folio = 'SATEG-' + str(new_id).zfill(4) + '/' + str(year)

                else:
                    folio = 'SATEG-0001/' + str(year)
            elif self.request.user.area == 'EJECUCION':
                if query != []:
                    query_id = str(query[0]['folio'])[15:20]
                    query_year = str(query[0]['folio'])[21:]
                    if year == int(query_year):
                        new_id = int(query_id) + 1
                    else:
                        new_id = 1
                else:
                    new_id = 1
                folio = 'SATEG-03-03-00-' + \
                    str(new_id).zfill(5) + '/' + str(year)
            else:
                query_id = str(query[0]['folio'])[15:19]
                query_year = str(query[0]['folio'])[20:]

                if year == int(query_year):
                    new_id = int(query_id) + 1
                else:
                    new_id = 1

                folio = 'SATEG-03-02-00-' + \
                    str(new_id).zfill(4) + '/' + str(year)

            return folio

        if request.POST['firma'] == '1':
            firma = 'FISICA'
        else:
            firma = 'DIGITAL'

        Oficios.objects.create(
            folio=get_folio(),
            nombre=request.POST['nombre'],
            puesto=request.POST['puesto'],
            asunto=request.POST['asunto'],
            dependencia=request.POST['dependencia'],
            fecha=datetime.date.today(),
            usuario=user,
            # enviado=str(send_by)[start:end],
            firma=firma,
            estatus='EN PROCESO'
        )
        instancia_oficio = Oficios.objects.latest('id')

        if request.POST['copia_a']:
            lista_usuarios = []
            copia_a = request.POST['copia_a'].split(',')

            for id in copia_a:
                instance_usuario = User.objects.get(id=str(id))
                cc = CC(
                    oficio=instancia_oficio,
                    user=instance_usuario,
                    visto=False
                )
                lista_usuarios.append(cc)

            CC.objects.bulk_create(lista_usuarios)

        messages.success(self.request, 'oficio')

        return redirect(reverse('oficios_app:panel', kwargs={"item": 1, "vista": 0})) #item 1   


class Modificar_Oficio(LoginRequiredMixin, TemplateView):
    template_name = 'oficios/modificar_oficio.html'

    def get_context_data(self, **kwargs):
        context = super(Modificar_Oficio, self).get_context_data(**kwargs)

        obj = Oficios.objects.get(id=self.kwargs.get('pk'))
        obj_cc = CC.objects.filter(oficio=self.kwargs.get('pk'))

        context['copia_a'] = obj_cc
        context['id_oficio'] = self.kwargs.get('pk')
        selected_firm = Codigos_Maestros.objects.filter(comentario=obj.firma)
        context['selected_firm'] = selected_firm[0].id

        context['folio'] = obj.folio
        context['fecha'] = obj.fecha
        context['nombre'] = obj.nombre
        context['asunto'] = obj.asunto
        context['puesto'] = obj.puesto
        context['dependencia'] = obj.dependencia
        context['comentarios'] = obj.comentarios

        if obj.pdf:
            context['pdf'] = obj.pdf.url
        else:
            context['pdf'] = None

        context['usuarios'] = User.objects.filter(
            is_superuser=False, is_active=True)
        context['form'] = NuevoOficioForm

        return context

    def post(self, request, *args, **kwargs):
        instancia = Oficios.objects.get(id=self.kwargs.get('pk'))

        fecha = request.POST['fecha']
        if request.POST['firma'] == '1':
            firma = 'FISICA'
        else:
            firma = 'DIGITAL'

        instancia.nombre = request.POST['nombre']
        instancia.puesto = request.POST['puesto']
        instancia.asunto = request.POST['asunto']
        instancia.dependencia = request.POST['dependencia']
        instancia.fecha = datetime.datetime(
            int(fecha[6:10]), int(fecha[3:5]), int(fecha[:2]))
        instancia.firma = firma

        filepath = request.FILES['pdf'] if 'pdf' in request.FILES else False
        if filepath != False:
            instancia.pdf = request.FILES['pdf']
            instancia.estatus = 'CONCLUIDO'

        if request.POST['copia_a']:
            copia_a = request.POST['copia_a'].split(',')

            # Filtrar usuarios actuales
            data = CC.objects.filter(oficio=instancia)

            for row in data:
                instance_user = User.objects.get(id=str(row.user.id))

                # eliminar usuarios del oficio
                if not str(instance_user.id) in copia_a:
                    instancia.copia_a.remove(instance_user)

            lista_usuarios = []
            for id in copia_a:

                # buscar si ya existe el usuario
                instancia_cc = CC.objects.filter(
                    oficio=self.kwargs.get('pk'),
                    user=str(id)
                )

                if not instancia_cc:
                    instance_usuario = User.objects.get(id=str(id))
                    cc = CC(
                        oficio=instancia,
                        user=instance_usuario,
                        visto=False
                    )
                    lista_usuarios.append(cc)

            CC.objects.bulk_create(lista_usuarios)

        instancia.save()

        messages.success(self.request, 'oficio')

        return redirect(self.request.META['HTTP_REFERER'])


class Recibir_Oficio(LoginRequiredMixin, TemplateView):
    template_name = 'oficios/recibir_oficio.html'

    def get_context_data(self, **kwargs):
        context = super(Recibir_Oficio, self).get_context_data(**kwargs)

        # Opcion para copiar a: solo muestra usuarios de la misma unidad responsable
        context['usuarios'] = User.objects.filter(
            is_superuser=False,
            is_active=True,
            unidad=self.request.user.unidad.id
        )

        #context['area'] = Codigos_Maestros.objects.filter(codigo='XXAREA')
        context['area'] = Areas.objects.filter(
            id=self.request.user.areas.id
        )

        context['para'] = User.objects.filter(
            is_superuser=False, is_active=True)
        context['todos'] = User.objects.filter(is_superuser=False)
        context['form'] = RecibirOficioForm

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user.username

        send_to = request.POST['para']
        area = request.POST['area']

        obj = User.objects.filter(id=str(send_to))
        obj2 = Areas.objects.filter(id=str(area))

        filepath = request.FILES['pdf'] if 'pdf' in request.FILES else False
        if filepath != False:
            pdf = request.FILES['pdf']
        else:
            pdf = ''

        fecha = request.POST['fecha']

        instancia_area = Areas.objects.get(id=self.request.user.unidad.id)

        Recibidos.objects.create(
            folio=request.POST['folio'],
            remitente=request.POST['remitente'],
            puesto=request.POST['puesto'],
            asunto=request.POST['asunto'],
            dependencia=request.POST['dependencia'],
            fecha=datetime.datetime(
                int(fecha[6:10]), int(fecha[3:5]), int(fecha[:2])),
            usuario=user,
            para=obj[0].username,
            area=obj2[0].nombre,
            firma='FISICA',
            comentarios=request.POST['comentarios'],
            estatus='EN PROCESO',
            cc_externas=request.POST['cc_externas'],
            pdf=pdf,
            unidad=instancia_area
        )
        instancia_oficio = Recibidos.objects.latest('id')

        # Guardar Copiar a
        if request.POST['copiar_a']:
            copiar_a = request.POST['copiar_a'].split(',')

            lista_usuarios = []
            for id in copiar_a:
                instance_usuario = User.objects.get(id=str(id))
                cco = CCO(
                    oficio=instancia_oficio,
                    user=instance_usuario,
                    visto=False,
                    tipo='C',  # Copia
                    enviado_por=user,
                    estatus='EN PROCESO'
                )
                lista_usuarios.append(cco)

            CCO.objects.bulk_create(lista_usuarios)

        messages.success(self.request, 'recibido')

        return redirect(self.request.META['HTTP_REFERER'])


class Editar_Oficio_Recibido(LoginRequiredMixin, TemplateView):
    template_name = 'oficios/editar_oficio_recibido.html'

    def get_context_data(self, **kwargs):
        context = super(Editar_Oficio_Recibido,
                        self).get_context_data(**kwargs)

        obj = Recibidos.objects.get(id=self.kwargs.get('pk'))

        obj_c = CCO.objects.filter(oficio=self.kwargs.get(
            'pk'), tipo='C', enviado_por=self.request.user.username)
        #obj_t = CCO.objects.filter(oficio = self.kwargs.get('pk'), tipo='T')

        context['copiar_a'] = obj_c
        #context['turnar_a'] = obj_t
        context['id_oficio'] = self.kwargs.get('pk')

        selected_area = Areas.objects.filter(nombre=obj.area)
        context['selected_area'] = selected_area[0].id
        selected_para = User.objects.filter(username=obj.para)
        context['selected_para'] = selected_para[0].id
        context['selected_user'] = selected_para[0].username

        context['folio'] = obj.folio
        context['fecha'] = obj.fecha
        context['remitente'] = obj.remitente
        context['asunto'] = obj.asunto
        context['puesto'] = obj.puesto
        context['dependencia'] = obj.dependencia
        context['comentarios'] = obj.comentarios
        context['cc_externas'] = obj.cc_externas

        if obj.pdf:
            context['pdf'] = obj.pdf.url
        else:
            context['pdf'] = ''

        #context['area'] = Codigos_Maestros.objects.filter(codigo='XXAREA')
        context['area'] = Areas.objects.filter(
            id=self.request.user.areas.id
        )

        context['para'] = User.objects.filter(
            is_superuser=False, is_active=True)
        context['todos'] = User.objects.filter(is_superuser=False)

        #context['usuarios'] = User.objects.filter(is_superuser=False, is_active=True)
        context['usuarios'] = User.objects.filter(
            is_superuser=False,
            is_active=True,
            unidad=self.request.user.unidad.id
        )

        context['form'] = RecibirOficioForm

        return context

    def post(self, request, *args, **kwargs):
        instancia = Recibidos.objects.get(id=self.kwargs.get('pk'))

        user = self.request.user.username

        send_to = request.POST['para']
        area = request.POST['area']

        obj = User.objects.filter(id=str(send_to))
        obj2 = Areas.objects.filter(id=str(area))
        fecha = request.POST['fecha']

        instancia.folio = request.POST['folio']
        instancia.remitente = request.POST['remitente']
        instancia.puesto = request.POST['puesto']
        instancia.asunto = request.POST['asunto']
        instancia.dependencia = request.POST['dependencia']
        instancia.fecha = datetime.datetime(
            int(fecha[6:10]), int(fecha[3:5]), int(fecha[:2]))
        instancia.para = obj[0].username
        instancia.area = obj2[0].nombre
        instancia.estatus = 'EN PROCESO'
        instancia.comentarios = request.POST['comentarios']
        instancia.cc_externas = request.POST['cc_externas']

        filepath = request.FILES['pdf'] if 'pdf' in request.FILES else False
        if filepath != False:
            instancia.pdf = request.FILES['pdf']

        if request.POST['copiar_a']:
            copiar_a = request.POST['copiar_a'].split(',')

            # Filtrar usuarios con copia
            data_c = CCO.objects.filter(
                oficio=instancia, tipo='C', enviado_por=user)

            for row in data_c:
                instance_user = User.objects.get(id=str(row.user.id))

                # eliminar usuarios del oficio
                if not str(instance_user.id) in copiar_a:
                    instancia.copiar_a.remove(instance_user)

            lista_usuarios = []
            for id in copiar_a:

                # buscar si ya existe el usuario
                instancia_cco = CCO.objects.filter(
                    oficio=self.kwargs.get('pk'),
                    user=str(id),
                    tipo='C',
                    enviado_por=user
                )

                if not instancia_cco:
                    instance_usuario = User.objects.get(id=str(id))
                    cco = CCO(
                        oficio=instancia,
                        user=instance_usuario,
                        visto=False,
                        tipo='C',
                        enviado_por=user,
                        estatus='EN PROCESO'
                    )
                    lista_usuarios.append(cco)

            CCO.objects.bulk_create(lista_usuarios)

        instancia.save()

        messages.success(self.request, 'recibido')

        return redirect(self.request.META['HTTP_REFERER'])


class Editar_Oficios(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Oficios
    template_name = 'oficios/editar_oficios.html'
    form_class = OficiosForm

    def form_valid(self, form):
        send_by = form.cleaned_data['enviado']
        start = str(send_by).find('(') + 1
        end = str(send_by).find(')')

        form.instance.enviado = str(send_by)[start:end]

        if form.instance.pdf:
            form.instance.estatus = 'CONCLUIDO'
        else:
            form.instance.estatus = 'EN PROCESO'

        messages.success(self.request, 'oficio')

        return super(Editar_Oficios, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(Editar_Oficios, self).get_context_data(**kwargs)

        context['usuarios'] = User.objects.filter(is_superuser=False)

        obj = self.get_object()
        selected = Codigos_Maestros.objects.filter(comentario=obj.firma)
        context['selected_firm'] = selected[0].id

        selected_enviado = User.objects.filter(username=obj.enviado)
        context['selected_enviado'] = selected_enviado[0].id

        return context

    def get_success_url(self):
        return reverse_lazy('oficios_app:correspondencia', kwargs={'item': 0, })


class Editar_Recibidos(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Recibidos
    template_name = 'oficios/editar_recibidos.html'
    form_class = RecibidosForm
    success_message = 'Folio actualizado exitosamente!'

    def form_valid(self, form):
        user = self.request.user.username

        send_to = form.cleaned_data['para']
        area = form.cleaned_data['area']

        obj = User.objects.filter(id=str(send_to))
        obj2 = Codigos_Maestros.objects.filter(id=str(area))

        if form.instance.pdf:
            form.instance.estatus = 'CONCLUIDO'
        else:
            form.instance.estatus = 'EN PROCESO'

        form.instance.para = obj[0].username
        form.instance.area = obj2[0].comentario

        return super(Editar_Recibidos, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(Editar_Recibidos, self).get_context_data(**kwargs)

        obj = self.get_object()
        selected_firm = Codigos_Maestros.objects.filter(comentario=obj.firma)
        context['selected_firm'] = selected_firm[0].id

        selected_area = Codigos_Maestros.objects.filter(comentario=obj.area)
        context['selected_area'] = selected_area[0].id

        selected_para = User.objects.filter(username=obj.para)
        context['selected_para'] = selected_para[0].id
        context['selected_user'] = selected_para[0].username

        context['area'] = Codigos_Maestros.objects.filter(codigo='XXAREA')
        context['para'] = User.objects.filter(is_superuser=False)
        context['todos'] = User.objects.filter(is_superuser=False)

        return context

    def get_success_url(self):
        return reverse_lazy('oficios_app:correspondencia', kwargs={'item': 0, })


class CrearPermisosView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Permisos
    template_name = 'oficios/alta_permisos.html'
    form_class = PermisosForm
    success_url = reverse_lazy(
        'oficios_app:correspondencia', kwargs={'item': 0, })
    success_message = 'Permisos asignados exitosamente!'

    def get_form_kwargs(self):
        kwargs = super(CrearPermisosView, self).get_form_kwargs()
        kwargs['username'] = self.request.user.username
        return kwargs


class CrearCompartidosView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Compartidos
    template_name = 'oficios/alta_compartidos.html'
    form_class = CompartidosForm

    def get_form_kwargs(self):
        kwargs = super(CrearCompartidosView, self).get_form_kwargs()
        kwargs['username'] = self.request.user.username
        kwargs['unidad'] = self.request.user.unidad.id
        return kwargs

    def form_valid(self, form):
        share_permissions = []

        id_user = self.request.user.id
        share_permissions = form.cleaned_data['compartidos']

        for data in User.objects.all():
            if Permisos.objects.filter(usuario__contains=data).exists():
                instance = Permisos.objects.get(usuario__contains=data)
                instance.permisos.remove(id_user)
                instance.save()

        for data in share_permissions:
            if Permisos.objects.filter(usuario__contains=data).exists():
                instance = Permisos.objects.get(usuario__contains=data)
                instance.permisos.add(id_user)
                instance.save()

        return super(CrearCompartidosView, self).form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class Ver_Recibidos(LoginRequiredMixin, DetailView):
    model = Recibidos
    template_name = 'oficios/ver_recibidos.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Recibidos, self).get_context_data(**kwargs)
        oficio = self.get_object()

        context['cc'] = CCO.objects.filter(
            oficio=oficio.id,
            tipo='C',
            enviado_por=self.request.user.username
        )
        context['turnados'] = CCO.objects.filter(
            oficio=oficio.id,
            tipo='T',
            enviado_por=self.request.user.username
        )

        context['origen'] = CCO.objects.filter(
            oficio=oficio.id,
            tipo='T',
            user=self.request.user.id
        )

        context['mis_copias'] = CCO.objects.filter(
            oficio=oficio.id,
            tipo='C',
            user=self.request.user.id
        )

        context['archivos'] = Archivos_Recibidos.objects.filter(
            oficio=oficio.id
        )

        return context


class Ver_Oficios(LoginRequiredMixin, DetailView):
    model = Oficios
    template_name = 'oficios/ver_oficios.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(Ver_Oficios, self).get_context_data(**kwargs)
        oficio = self.get_object()

        context['cc'] = CC.objects.filter(oficio=oficio.id)

        context['archivos'] = Archivos_Oficios.objects.filter(
            oficio=oficio.id
        )

        return context


class Visto(View):

    def get(self, request, *args, **kwargs):

        id_oficio = self.kwargs.get('id_oficio')
        id_user = self.kwargs.get('id_user')
        tipo = self.kwargs.get('tipo')

        if CCO.objects.filter(oficio=id_oficio, user=id_user).exists():
            # instancia = CCO.objects.get(
            #     oficio = id_oficio,
            #     user = id_user,
            #     tipo = tipo
            # )
            # instancia.visto = True
            # instancia.fecha_visto = datetime.date.today()
            # instancia.save()

            CCO.objects.filter(
                oficio=id_oficio,
                user=id_user,
                tipo=tipo
            ).update(
                visto=True,
                fecha_visto=datetime.date.today()
            )

        return JsonResponse({'res': 'ok'})


class Visto_Oficio(View):

    def get(self, request, *args, **kwargs):

        id_oficio = self.kwargs.get('id_oficio')
        id_user = self.kwargs.get('id_user')

        if CC.objects.filter(oficio=id_oficio, user=id_user).exists():
            # instancia = CC.objects.get(
            #     oficio = id_oficio,
            #     user = id_user
            # )
            # instancia.visto = True
            # instancia.save()

            CC.objects.filter(
                oficio=id_oficio,
                user=id_user
            ).update(
                visto=True
            )

        return JsonResponse({'res': 'ok'})


class Cmmt_Oficio(View):

    def post(self, request, *args, **kwargs):

        id_oficio = self.kwargs.get('id_oficio')
        id_user = self.kwargs.get('id_user')

        if CC.objects.filter(oficio=id_oficio, user=id_user).exists():
            instancia = CC.objects.get(
                oficio=id_oficio,
                user=id_user
            )
            instancia.comentarios = request.POST['comentarios']
            instancia.save()

        return JsonResponse({'res': 'ok'})


class Cmmt_Recibido(View):

    def post(self, request, *args, **kwargs):

        id_oficio = self.kwargs.get('id_oficio')
        id_user = self.kwargs.get('id_user')

        if CCO.objects.filter(oficio=id_oficio, user=id_user).exists():
            instancia = CCO.objects.get(
                oficio=id_oficio,
                user=id_user,
                tipo='C'
            )
            instancia.comentarios = request.POST['comentarios']
            instancia.save()

        return JsonResponse({'res': 'ok'})


class Declinar_Recibido(View):

    def post(self, request, *args, **kwargs):

        id_oficio = self.kwargs.get('id_oficio')
        id_user = self.kwargs.get('id_user')

        if CCO.objects.filter(oficio=id_oficio, user=id_user, tipo='T').exists():
            instancia = CCO.objects.get(
                oficio=id_oficio,
                user=id_user,
                tipo='T'
            )

            instancia.declinado = True
            instancia.comentarios = ''
            instancia.visto = False
            instancia.respuesta = False
            instancia.archivo = ''
            instancia.estatus = 'EN PROCESO'
            instancia.observaciones = request.POST['comentarios']
            instancia.save()

        return JsonResponse({'res': 'ok'})


class Turnar(LoginRequiredMixin, TemplateView):
    template_name = 'oficios/turnar.html'

    def get_context_data(self, **kwargs):
        context = super(Turnar, self).get_context_data(**kwargs)

        instancia = Recibidos.objects.get(id=self.kwargs.get('pk'))

        user = self.request.user.username
        obj_t = CCO.objects.filter(
            oficio=self.kwargs.get('pk'),
            tipo='T',
            enviado_por=user
        )

        obj_c = CCO.objects.filter(
            oficio=self.kwargs.get('pk'),
            tipo='C',
            enviado_por=user
        )

        if instancia.fecha_vencimiento:
            context['fecha_vencimiento'] = instancia.fecha_vencimiento
        else:
            context['fecha_vencimiento'] = None

        if obj_t:
            context['comentarios'] = obj_t[0].observaciones
        else:
            context['comentarios'] = ''
        context['id_oficio'] = self.kwargs.get('pk')

        #context['usuarios'] = User.objects.filter(is_superuser=False, is_active=True)
        context['usuarios'] = User.objects.filter(
            is_superuser=False,
            is_active=True,
            unidad=self.request.user.unidad.id
        )

        context['turnar_a'] = obj_t
        context['copiar_a'] = obj_c
        context['form'] = TurnarForm

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user.username
        instancia_oficio = Recibidos.objects.get(id=self.kwargs.get('pk'))

        cmmt = request.POST['comentarios']

        fecha = request.POST.get('fecha_vencimiento', '')

        if fecha != '':
            #fecha = request.POST['fecha_vencimiento']
            instancia = Recibidos.objects.get(id=self.kwargs.get('pk'))

            instancia.fecha_vencimiento = datetime.datetime(
                int(fecha[6:10]), int(fecha[3:5]), int(fecha[:2]))

            instancia.save()

        if request.POST['copiar_a']:
            copiar_a = request.POST['copiar_a'].split(',')

            # Filtrar usuarios con copia
            data_c = CCO.objects.filter(
                oficio=instancia_oficio, tipo='C', enviado_por=user)

            for row in data_c:
                instance_user = User.objects.get(id=str(row.user.id))

                # eliminar usuarios del oficio
                if not str(instance_user.id) in copiar_a:
                    instancia_oficio.copiar_a.remove(instance_user)

            lista_usuarios = []
            for id in copiar_a:

                # buscar si ya existe el usuario
                instancia_cco = CCO.objects.filter(
                    oficio=self.kwargs.get('pk'),
                    user=str(id),
                    tipo='C',
                    enviado_por=user
                )

                if not instancia_cco:
                    instance_usuario = User.objects.get(id=str(id))
                    cco = CCO(
                        oficio=instancia_oficio,
                        user=instance_usuario,
                        visto=False,
                        tipo='C',
                        enviado_por=user,
                        estatus='EN PROCESO'
                    )
                    lista_usuarios.append(cco)

            CCO.objects.bulk_create(lista_usuarios)
        else:
            # borrar registros
            data_c = CCO.objects.filter(
                oficio=instancia_oficio, tipo='C', enviado_por=user)
            for row in data_c:
                row.delete()

        if request.POST['turnar_a']:
            turnar_a = request.POST['turnar_a'].split(',')
            # Filtrar usuarios turnados
            data_t = CCO.objects.filter(
                oficio=instancia_oficio, tipo='T', enviado_por=user)

            for row in data_t:
                instance_user = User.objects.get(id=str(row.user.id))

                # eliminar usuarios del oficio
                if not str(instance_user.id) in turnar_a:
                    instancia_oficio.copiar_a.remove(instance_user)

            lista_turnar = []
            for id in turnar_a:

                # buscar si ya existe el usuario
                instancia_cco = CCO.objects.filter(
                    oficio=self.kwargs.get('pk'),
                    user=str(id),
                    tipo='T',
                    enviado_por=user
                )

                if not instancia_cco:
                    instance_usuario = User.objects.get(id=str(id))
                    cco = CCO(
                        oficio=instancia_oficio,
                        user=instance_usuario,
                        visto=False,
                        tipo='T',
                        enviado_por=user,
                        estatus='EN PROCESO',
                        observaciones=cmmt
                    )
                    lista_turnar.append(cco)

            CCO.objects.bulk_create(lista_turnar)

        else:
            # borrar registros
            data_c = CCO.objects.filter(
                oficio=instancia_oficio, tipo='T', enviado_por=user)
            for row in data_c:
                row.delete()

        messages.success(self.request, 'recibido')
        return redirect(self.request.META['HTTP_REFERER'])


class Eliminar_Archivo(View):

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        opcion = self.kwargs.get('option')

        # Opcion 1 carga en Recibidos
        if opcion == 1:
            instancia_oficio = Archivos_Recibidos.objects.get(pk=pk)
            instancia_oficio.delete()

        # Opcion 0 carga en Oficios
        else:
            instancia_oficio = Archivos_Oficios.objects.get(pk=pk)
            instancia_oficio.delete()

        return JsonResponse({'res': 'ok'})


class Get_Files(View):

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get('pk')
        opcion = self.kwargs.get('option')

        data = []
        if opcion == 1:
            lista = []
            for row in Archivos_Recibidos.objects.filter(oficio=pk):
                data_file = {}
                data_file['id'] = row.id
                data_file['url'] = row.archivo.url
                data_file['nombre'] = row.archivo.name[21:]
                data_file['size'] = row.archivo.size
                lista.append(data_file)

            data = json.dumps(lista)
        else:
            lista = []
            for row in Archivos_Oficios.objects.filter(oficio=pk):
                data_file = {}
                data_file['id'] = row.id
                data_file['url'] = row.archivo.url
                data_file['nombre'] = row.archivo.name[21:]
                data_file['size'] = row.archivo.size
                lista.append(data_file)

            data = json.dumps(lista)

        return HttpResponse(data, 'application/json')


class Subir_Archivos(TemplateView):
    template_name = 'oficios/subir_archivos.html'

    def get_context_data(self, **kwargs):
        context = super(Subir_Archivos, self).get_context_data(**kwargs)

        pk = self.kwargs.get('pk')
        opcion = self.kwargs.get('option')

        context['option'] = opcion
        context['pk'] = pk

        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        opcion = self.kwargs.get('option')

        # Opcion 1 carga en Recibidos
        if opcion == 1:
            instancia_oficio = Recibidos.objects.get(pk=pk)

            archivo = request.FILES['file']

            Archivos_Recibidos(
                oficio=instancia_oficio,
                archivo=archivo
            ).save()

        # Opcion 2 carga en Oficios
        else:
            instancia_oficio = Oficios.objects.get(pk=pk)

            archivo = request.FILES['file']

            Archivos_Oficios(
                oficio=instancia_oficio,
                archivo=archivo
            ).save()

        return JsonResponse({'res': 'ok'})
