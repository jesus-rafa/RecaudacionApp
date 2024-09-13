import csv
from django.db import connection
from applications.users.forms import BatchForm, LoginForm, UserForm
from applications.users.models import Plantilla, User
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView


class UpdatePassword(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('home_app:home')
    template_name = 'app/change-password.html'
    template_name = 'users/update.html'


class Perfil(LoginRequiredMixin, UpdateView):   
    model = User
    template_name = 'users/perfil.html'
    form_class = UserForm
    success_message = 'Actualizado exitosamente!'

    def get_context_data(self, **kwargs):
        context = super(Perfil, self).get_context_data(**kwargs)

        user = self.request.user.username
        context['perfil'] = User.objects.filter(username=user)

        return context

    def get_success_url(self):
        return reverse_lazy('users_app:perfil', kwargs={'pk': self.object.id})


class Directorio(LoginRequiredMixin, TemplateView):
    template_name = 'users/directorio.html'
    
    def get_context_data(self, **kwargs):
        context = super(Directorio, self).get_context_data(**kwargs)

        cursor = connection.cursor()
        sql = f'''SELECT * FROM global_users;'''
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        queryset = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            queryset.append(dict(rowset))

        context['directorio'] = queryset
        
        return context


class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        user = authenticate(
            email=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )

        login(self.request, user)

        return super(LoginUser, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home_app:home')


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)

        return HttpResponseRedirect(
            reverse(
                'users_app:login'
            )
        )


class PlantillaView(View):

    def post(self, request, *args, **kwargs):
        user = self.request.user
        instance = Plantilla.objects.get(user=user.id)

        formData = request.POST

        for key, value in formData.items():
            if key == 'orientacion':
                instance.orientacion = value
            if key == 'barra':
                instance.barra = value
            if key == 'menu':
                instance.menu = value
            if key == 'reset':
                instance.orientacion = 0
                instance.menu = 0
                instance.bara = 0

        instance.save()

        return JsonResponse({'res': 'ok'})


class Batch_Users(TemplateView):
    template_name = 'users/users_batch.html'

    def get_context_data(self, **kwargs):
        context = super(Batch_Users, self).get_context_data(**kwargs)

        context['Formulario'] = BatchForm

        return context

    def post(self, request, *args, **kwargs):
        path = settings.MEDIA_ROOT + '/batch/test.csv'

        def handle_uploaded_file(file):
            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        def execute_batch(file):
            with open(path, 'r') as file:
                reader = csv.DictReader(
                    file, delimiter=',', quoting=csv.QUOTE_NONE)

                for row in reader:
                    row_values = []   
                    for field in reader.fieldnames:
                        row_values.append(row[field])
                    
                    if not User.objects.filter(email=row_values[0].strip()).exists():
                        User.objects.create_user(
                            row_values[0].strip(), # email
                            row_values[1].strip(), # nombres
                            row_values[2].strip(), # apellidos
                            row_values[3].strip() # password
                        )

                        instance_user = User.objects.last()

                        Plantilla.objects.create(
                            user=instance_user
                        )

        if request.method == 'POST':
            form = BatchForm(request.POST, request.FILES)
            if form.is_valid():
                handle_uploaded_file(request.FILES['archivo'])

                execute_batch(request.FILES['archivo'])

                messages.info(self.request, 'Usuarios cargados')

                return redirect(self.request.META['HTTP_REFERER'])
        else:
            form = BatchForm()  

        
