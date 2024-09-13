import re

from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import View
from .models import User
from applications.users.models import Accesos
from django.contrib.auth.models import Permission
from django.http import HttpResponseForbidden



# def check_acces(perfil, full_path):

    # flag = False
    # if perfil == 'ADMIN':
        # flag = True
    # else:
        # if str(full_path).find('?') > 0:
            # delimit = str(full_path).find('?')
            # path_access = str(full_path[:delimit])
        # else:
            # path_access = full_path
        
        # QuerySet = Accesos.objects.filter(perfil__in=perfil)

        # for page in QuerySet:
            # for url in page.urls.all():
                # if str(url) == str(path_access):
                    # #print(str(url) + '=>' + str(full_path[:delimit]))
                    # flag = True

    # return flag
    
def check_acces(perfil, full_path):

    if perfil == 'ADMIN':
        flag = True
    else:
        # devuelve la url sin parametros busca 2 diagonales
        try:
            match = re.search('(.*?/.*?)/', full_path)
            absolute_url = match.group()
        except Exception as e:
            absolute_url = full_path

        QuerySet = Accesos.objects.filter(perfil__in=perfil)

        flag = False
        for page in QuerySet:
            if page.urls.filter(url__icontains=absolute_url).exists():
                flag = True

    return flag
    

def check_permission(perfil, *permissions):

    check = Permission.objects.filter(
        group__in=perfil,
        codename__in=permissions
    )

    flag = False
    if check:
        flag = True

    return flag



class GlobalMixin(LoginRequiredMixin):
    login_url = reverse_lazy('users_app:login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        perfil = []
        for group in request.user.groups.all():
            perfil.append(group.id)

        if not check_acces(perfil, request.get_full_path()):
            # no tiene autorizacion
            return HttpResponseRedirect(
                reverse(
                    'users_app:login'
                )
            )

        return super().dispatch(request, *args, **kwargs)
        

class CRUDMixin(LoginRequiredMixin):
    login_url = reverse_lazy('users_app:login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        perfil = []
        for group in request.user.groups.all():
            perfil.append(group.id)

        if not check_permission(perfil, self.permission_required):
            return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)

