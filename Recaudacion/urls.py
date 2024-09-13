"""Recaudacion URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from applications.home.views import Error404View, Error505View
from .routers import router


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('accounts/', include('allauth.urls')),
    
    re_path('', include('applications.home.urls')),
    re_path('', include('applications.users.urls')),
    re_path('', include('applications.oficios.urls')),
    re_path('', include('applications.programacion.urls')),
    re_path('', include('applications.rec.urls')),
    re_path('', include('applications.padrones.urls')),
    re_path('', include('applications.transferidos.urls')),
    re_path('', include('applications.promocion.urls')),
    re_path('', include('applications.direccion.urls')),
    re_path('', include('applications.juridico.urls')),
    re_path('', include('applications.quinielas.urls')),
    re_path('', include('applications.saladejuntas.urls')),
    re_path('', include('applications.tramites.urls')),
    re_path('', include('applications.verificacion_vehicular.urls')),
    
    path('api/', include(router.urls)),
    path('modelos/', TemplateView.as_view(template_name='programacion/modelos.html')),
    re_path('ckeditor/', include('ckeditor_uploader.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = Error404View.as_view()
handler500 = Error505View.as_error_view()
