from datetime import date, datetime
import xmltodict
import requests
import json
import ast
from django.db import connection
from django.shortcuts import render
from django.views.generic import (TemplateView,ListView,CreateView,UpdateView)

from .models import Historial_Busqueda
from .functions import get_data_vehiculo

from applications.users.models import User
from applications.programacion.functions import General_Excel_ORM
from applications.rec.functions import generar_excel_orm


class VerificacionVehicular(TemplateView):   
    template_name = 'verificacion_vehicular/verificacion.html'

    def get_context_data(self, **kwargs):
        context = super(VerificacionVehicular, self).get_context_data(**kwargs)  
        serie = self.kwargs.get('no_serie')    

        context["busqueda_no_serie"] = ""           
        if serie and serie != 'busqueda':
            context["busqueda_no_serie"] = serie
            user_instance = User.objects.get(pk=self.request.user.id)
            Historial_Busqueda.objects.create(
                busqueda = serie,
                usuario = user_instance
            ).save()       

        context["info_verificacion_vehicular"] = get_data_vehiculo(self, serie, "11")
        context["historial_verificacion_vehicular"] = Historial_Busqueda.objects.filter(busqueda=serie).order_by("-modified")

        context["pefil_admin"] = False  
        if User.objects.filter(username=self.request.user.username, groups__name__in=['VERIFICACION ADMIN']).exists():
                context["pefil_admin"] = True

        return context

def ExportarHistorialBusquedasVerif(request, no_serie):
    busqueda = no_serie

    query = f'''
    SELECT 
        vvsb.created as fecha_busqueda,
        vvsb.busqueda as no_serie,
        CONCAT(uu.nombres, ' ', uu.apellidos) as usuario
    FROM verificacion_vehicular_historial_busqueda vvsb
    LEFT JOIN users_user uu ON uu.id = vvsb.usuario_id
    WHERE vvsb.busqueda = '{busqueda}';
    '''
    
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

    return generar_excel_orm(request, "reporte_historial_busquedas_verificacion.csv", queryset, fieldnames)
