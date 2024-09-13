from django.shortcuts import render
from django.db.models import Q, Sum, F
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    ListView
)

from applications.programacion.models import Programa
from applications.rec.models import Fiscalizados
from applications.users.mixins import GlobalMixin, CRUDMixin



class Direccion(GlobalMixin, ListView):
    template_name = 'direccion/direccion.html'
    model = Programa
    context_object_name = 'informativas'
    
    def get_queryset(self):
        return Programa.objects.filter(estatus = 'INFORMATIVAS')

    
    def get_context_data(self, **kwargs):
        context = super(Direccion, self).get_context_data(**kwargs)  
        
        context['fiscalizados'] = Fiscalizados.objects.all()
        return context
        
    