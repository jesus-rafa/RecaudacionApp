import datetime
from datetime import date, timedelta
from unittest import result
from dateutil.relativedelta import relativedelta

import os
import csv
from django.db.models import query
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
import xmltodict
import requests
import qrcode
import uuid
import json
from django.conf import settings
from itertools import chain
from django.http.response import JsonResponse
from django.contrib import messages
from django.views.generic.base import TemplateView

from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.core.serializers import serialize
from django.http.response import JsonResponse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView
)
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from applications.rec.models import Contacto, REC, Obligaciones, BP, Cartas_Invitacion, Fiscalizados, Busquedas, Registro_Civil, REC_Notificados, Circulo_Credito, Temporal_Circulo_Credito, Historial_Reporte_Circulo_Credito
from applications.home.models import Codigos_Maestros

from .forms import ContactoForm, BatchForm
from .functions import generar_excel_orm, validar_permite_consultar_expediente
from applications.users.models import User

from django.shortcuts import render, redirect

from django.db.models import Q, CharField, Value, F, Case, When
from django.db.models.functions import Cast,ExtractYear

from django.db import connection

from applications.programacion.models import Programa, Detalle, Archivos, Pagos, Contribuyentes
from applications.padrones.models import Programa_Padrones, Detalle_Padrones, Archivos_Padrones, Pagos_Padrones
from applications.transferidos.models import Programa_Transferidos, Detalle_Transferidos, Archivos_Transferidos, Pagos_Transferidos

from applications.users.mixins import GlobalMixin, CRUDMixin
from rest_framework.generics import ListAPIView
from .serializers import REC_Serializer, Circulo_Credito_Serializer
from.models import Circulo_Credito


class Registro_Civil_New(GlobalMixin, TemplateView):
    template_name = 'rec/registro_civil.html'
    context_object_name = 'response'
    
    def create_QRCode(self, input_data):

        name = self.request.user.username + \
            '__' + str(uuid.uuid1()) + '.png'

        path = settings.MEDIA_ROOT + '/media/qrcode/' + name
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(input_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(path)

        return name
        

    def get_context_data(self, **kwargs):
        context = super(Registro_Civil_New, self).get_context_data(**kwargs)

        tipo = self.request.GET.get("tipo")
        curp = self.request.GET.get("curp", '').strip()
        nombres = self.request.GET.get("nombres", '').strip()
        primer_apellido = self.request.GET.get("primer_apellido", '').strip()
        segundo_apellido = self.request.GET.get("segundo_apellido", '').strip()
        dia = self.request.GET.get("dia", '').strip()
        mes = self.request.GET.get("mes", '').strip()
        ano = self.request.GET.get("ano", '').strip()
        
        search = '|' + nombres + '|' + primer_apellido + '|' + segundo_apellido + '|' + dia + '|' + mes + '|' + ano + '|'

        if curp and str(tipo) == "1":
            messages.success(self.request, 'Defun')

            url = "https://securitywsqa.guanajuato.gob.mx:443/sst/Pruebas.QA_SG_SFIA_RegistroCivil_ActaDefunciones_AP?WSDL"
            xml = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:tem=\"http://tempuri.org/\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n      <tem:Defun>\r\n         <!--Optional:-->\r\n         <tem:Clave></tem:Clave>\r\n         <!--Optional:-->\r\n         <tem:Nombre></tem:Nombre>\r\n         <!--Optional:-->\r\n         <tem:ApPaterno></tem:ApPaterno>\r\n         <!--Optional:-->\r\n         <tem:ApMaterno></tem:ApMaterno>\r\n         <!--Optional:-->\r\n         <tem:Municipio></tem:Municipio>\r\n         <!--Optional:-->\r\n         <tem:Curp>" + \
                curp + "</tem:Curp>\r\n         <!--Optional:-->\r\n         <tem:FechaReg></tem:FechaReg>\r\n         <!--Optional:-->\r\n         <tem:opcion>dif</tem:opcion>\r\n      </tem:Defun>\r\n   </soapenv:Body>\r\n</soapenv:Envelope>"
            headers = {
                'Content-Type': 'text/xml',
                'SOAPAction': 'http://tempuri.org/Defun',
                'Authorization': 'Basic *****='
            }

            try:
                response = requests.post(url, headers=headers, data=xml)
                dictionary = xmltodict.parse(response.text)

                data = None
                new_data = dict()
                document = dict()
                for key, value in dictionary.items():
                    for key2, value2 in value.items():
                        if key2 == 'soap:Body':
                            for key3, value3 in value2.items():
                                if key3 == 'DefunResponse':
                                    for key4, value4 in value3.items():
                                        if key4 == 'DefunResult':
                                            for key5, value5 in value4.items():
                                                if key5 == 'Defunciones':
                                                    data = dict(value5)
                
                input_data = '|'
                for key, value in data.items():
                    if key == 'DifCurp':
                        new_data['CURP'] = value
                        input_data += value + '|'
                    if key == 'DifNombre':
                        new_data['Nombre(s)'] = value
                        input_data += value + '|'
                    if key == 'DifApPaterno':
                        new_data['Primer apellido'] = value
                        input_data += value + '|'
                    if key == 'DifApMaterno':
                        new_data['Segundo apellido'] = value
                        input_data += value + '|'
                    if key == 'DifSexoId':
                        new_data['Sexo'] = value
                        input_data += value + '|'
                    if key == 'DifFechaNac':
                        new_data['Fecha de nacimiento'] = value
                        input_data += value + '|'
                    if key == 'DifestadoIdNac':
                        new_data['Entidad de nacimiento'] = value
                        input_data += value + '|'
                    if key == 'DefuncionId':
                        new_data['Documento probatorio'] = 'ACTA DE DEFUNCION'
                        input_data += value + '|ACTA DE DEFUNCION|'

                for key, value in data.items():
                    if key == 'FechaReg':
                        document['Fecha registro'] = value
                        input_data += value + '|'
                    if key == 'ActaNum':
                        document['Número de acta'] = value
                        input_data += value + '|'
                    if key == 'EstadoIdReg':
                        document['Entidad de registro'] = value
                        input_data += value + '|'
                    if key == 'DifCiudadNac':
                        document['Municipio de registro'] = value
                        input_data += value + '|'

                
                context['response'] = new_data
                context['document'] = document
                context['data'] = data

                if data != None:
                    successs = True
                else:
                    successs = False
                    
                if len(input_data) > 1:
                    input_data += '__' + self.request.user.username

                    context['qrcode2'] = self.create_QRCode(input_data)
                    context['input_data'] = input_data
                else:
                    context['qrcode2'] = None
                    
                

            except:
                context = None
                successs = False

            Registro_Civil.objects.create(
                busqueda=curp,
                usuario=self.request.user.username,
                fecha=datetime.date.today(),
                is_success=successs
            )

        if str(tipo) == "2":
            messages.success(self.request, 'Nactos')

            url = "https://securitywsqa.guanajuato.gob.mx:443/sst/Pruebas.QA_SG_SFIA_RegistroCivil_ActaNacimientos_AP?WSDL"
            xml = "<Envelope xmlns=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n    <Body>\r\n        <Nactos xmlns=\"http://tempuri.org/\">\r\n            <Crip></Crip>\r\n            <Nombre>" + nombres.upper() + "</Nombre>\r\n            <ApPaterno>" + primer_apellido.upper() + "</ApPaterno>\r\n            <ApMaterno>" + \
                segundo_apellido.upper() + "</ApMaterno>\r\n            <Municipio></Municipio>\r\n            <Curp></Curp>\r\n            <FechaNacimiento>" + \
                dia + "/" + mes + "/" + ano + \
                "</FechaNacimiento>\r\n            <opcion>Reg</opcion>\r\n        </Nactos>\r\n    </Body>\r\n</Envelope>"

            headers = {
                'Content-Type': 'text/xml',
                'SOAPAction': 'http://tempuri.org/Nactos',
                'Authorization': 'Basic a2lvc2Nvc1pvbmFaZXJvOktpb3NjMHNab25AMDIwMTc='
            }

            try:
                response = requests.post(url, headers=headers, data=xml)
                dictionary = xmltodict.parse(response.text)

                nactos = None
                new_data = dict()
                document = dict()

                for key, value in dictionary.items():
                    for key2, value2 in value.items():
                        if key2 == 'soap:Body':
                            for key3, value3 in value2.items():
                                if key3 == 'NactosResponse':
                                    for key4, value4 in value3.items():
                                        if key4 == 'NactosResult':
                                            for key5, value5 in value4.items():
                                                if key5 == 'Nacimientos':
                                                    # value5 = lista ó dict ?
                                                    nactos = dict(value5)
                
                input_data = '|'
                for key, value in nactos.items():
                    if key == 'Curp':
                        new_data['CURP'] = value
                        input_data += value + '|'
                    if key == 'RegNombre':
                        new_data['Nombre(s)'] = value
                        input_data += value + '|'
                    if key == 'RegApPaterno':
                        new_data['Primer apellido'] = value
                        input_data += value + '|'
                    if key == 'RegApMaterno':
                        new_data['Segundo apellido'] = value
                        input_data += value + '|'
                    if key == 'RegSexoId':
                        new_data['Sexo'] = value
                        input_data += value + '|'
                    if key == 'RegFechaNac':
                        new_data['Fecha de nacimiento'] = value
                        input_data += value + '|'
                    if key == 'EstadoIdReg':
                        new_data['Entidad de nacimiento'] = value
                        input_data += value + '|'
                    if key == 'NactoId':
                        new_data['Documento probatorio'] = 'ACTA DE NACIMIENTO'
                        input_data += value + '|ACTA DE NACIMIENTO|'

                for key, value in nactos.items():
                    if key == 'FechaReg':
                        document['Fecha registro'] = value
                        input_data += value + '|'
                    if key == 'ActaNum':
                        document['Número de acta'] = value
                        input_data += value + '|'
                    if key == 'EstadoIdReg':
                        document['Entidad de registro'] = value
                        input_data += value + '|'
                    if key == 'DifCiudadNac':
                        document['Municipio de registro'] = value
                        input_data += value + '|'

                
                context['nac_response'] = new_data
                context['nac_document'] = document
                context['data2'] = nactos

                if nactos != None:
                    successs = True
                else:
                    successs = False
                    
                if len(input_data) > 1:
                    input_data += '__' + self.request.user.username

                    context['qrcode1'] = self.create_QRCode(input_data)
                    context['input_data'] = input_data
                else:
                    context['qrcode1'] = None

            except:
                context = None
                successs = False

            Registro_Civil.objects.create(
                busqueda=search,
                usuario=self.request.user.username,
                fecha=datetime.date.today(),
                is_success=successs
            )

        
        
        return context


class Lista_Contacto(GlobalMixin, ListView):
    template_name = 'rec/lista_contacto.html'
    context_object_name = 'contactos'

    def get_queryset(self):
        kword = self.request.GET.get("kword", '')
        return REC.objects.buscar_rfc(kword)

    def get_data(self, rfc, opcion):

        url = "http://172.31.113.187:180/Informacion_Contribuyente.asmx?op=Obtiene_Informacion"
        headers = {
            'Content-Type': 'text/xml',
            'SOAPAction': 'http://tempuri.org/Obtiene_Informacion'
        }
        xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n  <soap:Body>\r\n    <Obtiene_Informacion xmlns=\"http://tempuri.org/\">\r\n      <rfc>" + rfc + "</rfc>\r\n      <opcion>" + str(opcion) + "</opcion>\r\n    </Obtiene_Informacion>\r\n  </soap:Body>\r\n</soap:Envelope>"
        
        response = requests.post(url, headers=headers, data=xml)
        dictionary = xmltodict.parse(response.text)

        for key, value in dictionary.items():
            for key2, value2 in value.items():
                if key2 == 'soap:Body':
                    for key3, value3 in value2.items():
                        if key3 == 'Obtiene_InformacionResponse':
                            for key4, value4 in value3.items():
                                if key4 == 'Obtiene_InformacionResult':
                                    result = json.loads(value4)

        return result['Table']

    def get_context_data(self, **kwargs):
        context = super(Lista_Contacto, self).get_context_data(**kwargs)

        kword = self.request.GET.get("kword", '')
        if REC.objects.buscar_rfc(kword).exists():
            contribuyente = REC.objects.buscar_rfc(kword)
            rfc = contribuyente[0].rfc
        else:
            rfc = self.request.GET.get("kword", '')
            
        context["permite_consultar_expediente"] = validar_permite_consultar_expediente(self.request.user.username)
        
        # Consultas a SQL Server para informacion del contribuyente
        if rfc:
            try:
                # Opcion 1 - Datos Generales SAT
                sat = self.get_data(rfc, 1)  
            except:
                sat = []

            try:
                # Opcion 2 - Datos Generales REC
                rec = self.get_data(rfc, 2)  
            except:
                rec = []

            try:
                # Opcion 4 - Obligaciones
                obligaciones = self.get_data(rfc, 4)  
            except:
                obligaciones = []

           
            try:
                # Opcion 5 - Regimen
                regimen = self.get_data(rfc, 5)  
            except:
                regimen = []

            try:
                # Opcion 6 - Vehiculos
                vehiculos = self.get_data(rfc[:10], 6)  
            except:
                vehiculos = []

            try:
                # Opcion 7 - Actividades
                actividades = self.get_data(rfc, 7)  
            except:
                actividades = []
            
            context['sat'] = sat
            context['rec'] = rec
            context['actividades'] = actividades
            context['obligaciones'] = obligaciones
            context['regimen'] = regimen
            context['vehiculos'] = vehiculos

        return context


class Ver_CFDI(LoginRequiredMixin, TemplateView):
    template_name = 'rec/ver_cfdi.html'

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

    def get_context_data(self, **kwargs):
        context = super(Ver_CFDI, self).get_context_data(**kwargs)

        id_cfdi = self.request.GET.get("pk", '')  

        # Consultas a SQL Server para CFDI
        try:
            # Opcion 1 - Retorna CFDI Master
            datos = self.get_data('', '', 5, id_cfdi) 

        except:
            datos = []
            
        context['cfdi'] = datos

        return context


class CFDI(LoginRequiredMixin, TemplateView):
    template_name = 'rec/cfdi.html'
    context_object_name = 'cfdi'

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

    def get_context_data(self, **kwargs):
        context = super(CFDI, self).get_context_data(**kwargs)

        kword = self.request.GET.get("kword", '')    
        busqueda_avanzada = self.request.GET.get("busqueda_avanzada", '')

        # Consultas a SQL Server para CFDI
        if kword:
            try:
                if busqueda_avanzada == 'on':
                    # Opcion 2 - Retorna CFDI Detalle
                    datos = self.get_data(kword, '', 2, 0) 
                else:
                    # Opcion 1 - Retorna CFDI Master
                    datos = self.get_data(kword, '', 1, 0) 
            except:
                datos = []
            
            context['cfdi'] = datos

        return context
        
        
class REC_Listado(GlobalMixin, TemplateView):
    template_name = 'rec/rec_listado.html'
    context_object_name = 'rec'

    def get_data(self, rfc, opcion):

        url = "http://172.31.113.187:180/Informacion_Contribuyente.asmx?op=Obtiene_Informacion"
        headers = {
            'Content-Type': 'text/xml',
            'SOAPAction': 'http://tempuri.org/Obtiene_Informacion'
        }
        xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n  <soap:Body>\r\n    <Obtiene_Informacion xmlns=\"http://tempuri.org/\">\r\n      <rfc>" + rfc + "</rfc>\r\n      <opcion>" + str(opcion) + "</opcion>\r\n    </Obtiene_Informacion>\r\n  </soap:Body>\r\n</soap:Envelope>"
        
        response = requests.post(url, headers=headers, data=xml)
        dictionary = xmltodict.parse(response.text)

        for key, value in dictionary.items():
            for key2, value2 in value.items():
                if key2 == 'soap:Body':
                    for key3, value3 in value2.items():
                        if key3 == 'Obtiene_InformacionResponse':
                            for key4, value4 in value3.items():
                                if key4 == 'Obtiene_InformacionResult':
                                    result = json.loads(value4)

        return result['Table']

    def get_context_data(self, **kwargs):
        context = super(REC_Listado, self).get_context_data(**kwargs)

        kword = self.request.GET.get("kword", '')

        context["permite_consultar_expediente"] = validar_permite_consultar_expediente(self.request.user.username)

        # Consultas a SQL Server para informacion del contribuyente
        if kword:
            try:
                # Opcion 8 - Retorna RFC y Nombre Todos los comunes
                datos = self.get_data(kword, 8)  
            except:
                datos = []
            
            context['rec'] = datos

        return context
        


class Lista_Contacto_2(GlobalMixin, ListView):
    template_name = 'rec/lista_contacto_2.html'
    context_object_name = 'contactos'

    # def get_context_data(self, **kwargs):
    #     context = super(Lista_Contacto_2, self).get_context_data(**kwargs)
    #     kword = self.request.GET.get("kword", '').strip()
    #     top = self.request.GET.get("top", '').strip()

    #     vigilancia = Programa.objects.filter(
    #         Q(rfc__icontains = kword) | Q(nombre__icontains = kword)
    #     ).values_list('rfc','nombre')

    #     programacion = Programa_Padrones.objects.filter(
    #         Q(rfc__icontains = kword) | Q(nombre__icontains = kword)
    #     ).values_list('rfc','nombre')

    #     transferencias = Programa_Transferidos.objects.filter(
    #         Q(rfc__icontains = kword) | Q(nombre__icontains = kword)
    #     ).values_list('rfc','nombre')

    #     cartas = Cartas_Invitacion.objects.filter(
    #         rfc__icontains = kword
    #     ).values_list('rfc','remesa')

    #     mergue = list(chain(vigilancia, programacion, transferencias, cartas))
        
    #     context['mergue'] = mergue

    #     return context

    def get_queryset(self):
        
        if self.request.GET.get("top", '') == '':
            top = 10
        else:
            top = self.request.GET.get("top", '')
            
        
        if self.request.GET.get("kword", '') == '':

            mySql = f"""
                SELECT rfc, nombre, direccion FROM (
                    SELECT 
                        CASE WHEN E.rfc is null
                            THEN rfc_
                            ELSE E.rfc
                        END AS rfc,
                        CASE WHEN E.nombre is null
                            THEN nombre_
                            ELSE E.nombre
                        END AS nombre,
                        CASE WHEN E.direccion is null
                            THEN direccion_
                            ELSE E.direccion
                        END AS direccion
                    FROM(SELECT 
                            A.rfc AS rfc_,
                            A.nombre AS nombre_,
                            A.direccion AS direccion_
                        FROM public.padrones_programa_padrones A
                        UNION
                        SELECT 
                            B.rfc AS rfc_,
                            B.nombre AS nombre_,
                            B.direccion AS direccion_
                        FROM public.programacion_programa B
                        UNION
                        SELECT 
                            C.rfc AS rfc_,
                            C.nombre AS nombre_,
                            C.direccion AS direccion_
                        FROM public.transferidos_programa_transferidos C
                        UNION
                        SELECT 
                            D.rfc AS rfc_,
                            '' AS nombre_,
                            '' AS direccion_
                        FROM public.rec_cartas_invitacion D
                    ) AS universe
                        LEFT JOIN public.rec_rec E
                            ON E.rfc = rfc_
                    LIMIT {top} 
                ) AS summary
                GROUP BY 
                    rfc,
                    nombre,
                    direccion
            """
          
            # mySql = f""" SELECT id, rfc, nombre, direccion, correo, telefono 
            #             FROM RFC_Con_Notificacion LIMIT {top} """
        else:
            kword = self.request.GET.get("kword", '').strip()
            
            # mySql = f""" SELECT id, rfc, nombre, direccion, correo, telefono 
            #             FROM RFC_Con_Notificacion 
            #                 WHERE rfc like '%{kword.upper()}%' or nombre like '%{kword.upper()}%' LIMIT {top} """

            mySql = f"""
                SELECT rfc, nombre, direccion FROM (
                    SELECT 
                        CASE WHEN E.rfc is null
                            THEN rfc_
                            ELSE E.rfc
                        END AS rfc,
                        CASE WHEN E.nombre is null
                            THEN nombre_
                            ELSE E.nombre
                        END AS nombre,
                        CASE WHEN E.direccion is null
                            THEN direccion_
                            ELSE E.direccion
                        END AS direccion
                    FROM(SELECT 
                            A.rfc AS rfc_,
                            A.nombre AS nombre_,
                            A.direccion AS direccion_
                        FROM public.padrones_programa_padrones A
                        UNION
                        SELECT 
                            B.rfc AS rfc_,
                            B.nombre AS nombre_,
                            B.direccion AS direccion_
                        FROM public.programacion_programa B
                        UNION
                        SELECT 
                            C.rfc AS rfc_,
                            C.nombre AS nombre_,
                            C.direccion AS direccion_
                        FROM public.transferidos_programa_transferidos C
                        UNION
                        SELECT 
                            D.rfc AS rfc_,
                            '' AS nombre_,
                            '' AS direccion_
                        FROM public.rec_cartas_invitacion D
                    ) AS universe
                        LEFT JOIN public.rec_rec E
                            ON E.rfc = rfc_
                        WHERE rfc_ like '%{kword.upper()}%' or E.nombre like '%{kword.upper()}%'
                        LIMIT {top} 
                ) AS summary
                GROUP BY 
                    rfc,
                    nombre,
                    direccion
            """

        cursor = connection.cursor()          
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        queryset = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            queryset.append(dict(rowset))

        return queryset


class EnvioMasivo(GlobalMixin, ListView):
    template_name = 'rec/envio_masivo.html'
    context_object_name = 'cartas'

    # def get_context_data(self, **kwargs):
    #     context = super(EnvioMasivo, self).get_context_data(**kwargs)
        
    #     fecha_actual = datetime.date.today().year

    #     if self.request.GET.get("month", 'TODOS') != 'TODOS':
    #         date_time_str = str(self.request.GET.get("year", '')) + '-' + str(self.request.GET.get("month", '')) + '-01'
    #         fecha_inicio = datetime.datetime.strptime(date_time_str, "%Y-%m-%d")
    #         fecha_fin = fecha_inicio + relativedelta(months=1) - relativedelta(days=1)

    #     elif self.request.GET.get("year", '') != '':
    #         fecha_inicio = '01-01-' + str(self.request.GET.get("year", ''))
    #         fecha_fin = '31-12-' + str(self.request.GET.get("year", ''))

    #     else:
    #         fecha_inicio = '01-01-' + str(fecha_actual)
    #         fecha_fin = '31-12-' + str(fecha_actual)

    #     context['inicio'] = fecha_inicio
    #     context['fin'] = fecha_fin

    #     return context

    def get_queryset(self):

        fecha_actual = datetime.date.today().year

        if self.request.GET.get("month", 'TODOS') != 'TODOS':
            date_time_str = str(self.request.GET.get("year", '')) + '-' + str(self.request.GET.get("month", '')) + '-01'
            fecha_inicio = datetime.datetime.strptime(date_time_str, "%Y-%m-%d")
            fecha_fin = fecha_inicio + relativedelta(months=1) - relativedelta(days=1)

        elif self.request.GET.get("year", '') != '':
            fecha_inicio = '01-01-' + str(self.request.GET.get("year", ''))
            fecha_fin = '31-12-' + str(self.request.GET.get("year", ''))

        else:
            fecha_inicio = '01-01-' + str(fecha_actual)
            fecha_fin = '31-12-' + str(fecha_actual)

        if self.request.GET.get("area", '') != 'TODAS':
            area = "WHERE area = '" + str(self.request.GET.get("area", '')) + "'"
        else:
            area = ''

        cursor = connection.cursor()
        mySql = f''' SELECT * FROM public.avance_mensual_programas_masivos('{fecha_inicio}','{fecha_fin}') {area}; '''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        
        return result


class CartasInvitacion(GlobalMixin, ListView):
    template_name = 'rec/cartas_invitacion.html'
    context_object_name = 'cartas'

    def get_queryset(self):
        kword = self.request.GET.get("kword", '')

        if kword:
            rec = REC.objects.filter(
                Q(rfc__icontains = kword) | Q(nombre__icontains = kword)
            )

            if rec:
                queryset = Cartas_Invitacion.objects.filter(
                    rfc__icontains=rec[0].rfc
                )
            else:
                queryset = Cartas_Invitacion.objects.filter(
                    rfc__icontains=kword
                )
        else:
            queryset = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CartasInvitacion, self).get_context_data(**kwargs)

        fecha_actual = datetime.date.today().year

        if self.request.GET.get("year", '') != '':
            fecha_inicio = str(self.request.GET.get("year", '')) + '-01-01'
            fecha_fin = str(self.request.GET.get("year", '')) + '-12-31'

        else:
            fecha_inicio = str(fecha_actual) + '-01-01'
            fecha_fin = str(fecha_actual) + '-12-31'
        
        context['todas'] = Cartas_Invitacion.objects.filter(
            fecha_envio__gte = fecha_inicio,
            fecha_envio__lte = fecha_fin
        ).values(
            'remesa', 'programa', 'fecha_envio'
        ).annotate(
            total=Count('programa')
        ).order_by('fecha_envio')

        context['total_cartas'] = Cartas_Invitacion.objects.filter(
            fecha_envio__gte = fecha_inicio,
            fecha_envio__lte = fecha_fin
        ).count()

        context['year'] = Cartas_Invitacion.objects.annotate(year=ExtractYear('fecha_envio')).values('year').distinct().order_by('year')


        return context


class ContribuyentesRevisados(GlobalMixin, ListView):
    template_name = 'rec/contribuyentes_revisados.html'
    context_object_name = 'individual'

    def get_queryset(self):
        kword = self.request.GET.get("kword", '')

        if kword:
            #queryset = Contribuyentes.objects.filter(rfc = kword)
            cursor = connection.cursor()
            mySql = f''' 
                SELECT 
                    ejercicio
                    , periodo
                    , rfc
                    , estatus
                    , procedente
                    , no_procedente
                    , usuario
                    , comentarios
                    , motivo
                    , tiempo
                    , fecha_fin
                    , fecha_inicio
                FROM 
                    public.contribuyentes_revisados
                WHERE 
                    rfc = '{kword}'
            '''
            cursor.execute(mySql)
            fieldnames = [name[0] for name in cursor.description]
            result = []
            for row in cursor.fetchall():
                rowset = []
                for field in zip(fieldnames, row):
                    rowset.append(field)
                result.append(dict(rowset))

            queryset = result
        else:
            queryset = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super(ContribuyentesRevisados, self).get_context_data(**kwargs)

        anio_actual = datetime.date.today().year
        periodo_actual = datetime.date.today().month
        condicion = "WHERE "

        if self.request.GET.get("year", '') != '' and self.request.GET.get("month", '') != '':             
            ejercicio = " EJERCICIO = " + str(self.request.GET.get("year", ''))
            periodo = "AND PERIODO = " + str(self.request.GET.get("month", ''))
        else:
            ejercicio = " EJERCICIO = " + str(anio_actual)
            periodo = "AND PERIODO = " + str(periodo_actual)

        if self.request.GET.get("year", '') == 'TODOS':
            ejercicio = ""
            periodo = "PERIODO = " + str(self.request.GET.get("month", ''))
        if self.request.GET.get("month", '') == 'TODOS':
            ejercicio = " EJERCICIO = " + str(self.request.GET.get("year", ''))
            periodo = ""
        if self.request.GET.get("year", '') == 'TODOS' and self.request.GET.get("month", '') == 'TODOS':
            ejercicio = ""
            periodo = ""
            condicion = ""
            

        cursor = connection.cursor()
        mySql = f''' 
            SELECT 
                EJERCICIO 
                , PERIODO 
                , COUNT(*) AS REVISADAS 
                , SUM(PROCEDENTE) AS PROCEDENTES 
                , SUM(NO_PROCEDENTE) AS NO_PROCEDENTES 
                , AVG(TIEMPO) AS DIAS
            FROM 
                CONTRIBUYENTES_REVISADOS
            {condicion}
                {ejercicio} {periodo}                 
            GROUP BY 
                EJERCICIO , PERIODO
         '''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))

        context['contribuyentes'] = result

        context['years'] =  Codigos_Maestros.objects.filter(codigo='XXYEAR').order_by('-valor')

        return context


def DescargarExcel(request, programa):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cartas.csv"'

    writer = csv.writer(response)
    writer.writerow(['Remesa', 'Fecha Envio', 'Folio', 'RFC', 'Programa', 'Estatus'])

    cartas = Cartas_Invitacion.objects.filter(
        programa=programa
    ).values_list('remesa', 'fecha_envio', 'folio', 'rfc', 'programa', 'estatus')

    for row in cartas:
        writer.writerow(row)

    return response
    
def DescargarExcelMasivo(request, programa, ejercicio, periodo, area):
    response = HttpResponse(content_type='text/csv')
    nombre_archivo = programa.replace('-', '/') + '_' + ejercicio + '-' + periodo + '.csv'
    response['Content-Disposition'] = 'attachment; filename=' + nombre_archivo

    date_time_str = str(ejercicio) + '-' + str(periodo) + '-01'
    fecha_inicio = datetime.datetime.strptime(date_time_str, "%Y-%m-%d")
    fecha_fin = fecha_inicio + relativedelta(months=1) - relativedelta(days=1)

    writer = csv.writer(response)
    writer.writerow(['Fecha', 'RFC', 'Nombre', 'Programa', 'Presuntiva', 'Recaudado', 'Estatus', 'Area'])

    result = Programa_Padrones.objects.filter(
        programa = programa.replace('-', '/'),
        fecha__gte = fecha_inicio,
        fecha__lte = fecha_fin,
        area = area
    ).values_list(
        'fecha', 
        'rfc', 
        'nombre', 
        'programa', 
        'presuntiva', 
        'recaudado', 
        'estatus',
        'area'
    )

    #result = list(cursor.fetchall())

    for row in result:
        writer.writerow(row)

    return response

def DescargarExcelContribuyentes(request, ejercicio, periodo):
    response = HttpResponse(content_type='text/csv')
    nombre_archivo = 'contribuyentes_' + ejercicio + '_' + periodo + '.csv'
    response['Content-Disposition'] = 'attachment; filename=' + nombre_archivo

    writer = csv.writer(response)
    writer.writerow(['Ejercicio','Periodo','RFC','Modelo','Estatus','Motivo','Comentarios','Fecha_Inicio','Fecha_Fin','Tiempo','Usuario'])

    cursor = connection.cursor()
    mySql = f''' SELECT 
                    ejercicio,
                    periodo,
                    rfc,
                    alias,
                    estatus,
                    motivo,
                    comentarios,
                    fecha_inicio,
                    fecha_fin,
                    tiempo,
                    usuario
                FROM public.contribuyentes_revisados 
                    WHERE ejercicio = {ejercicio} AND periodo = {periodo}; '''
    cursor.execute(mySql)
    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        for field in zip(fieldnames, row):
            rowset.append(field[1])

        result.append(rowset)

    for row in result:
        writer.writerow(row)

    return response


class Alta_Datos(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    #permission_required = ('add_contacto')
    
    model = Contacto
    template_name = 'rec/alta_datos.html'
    form_class = ContactoForm
    success_message = 'Datos cargados!'
    
    def get_context_data(self, **kwargs):
        context = super(Alta_Datos, self).get_context_data(**kwargs)
        context['id_rfc'] = self.kwargs['rfc']
        context['programa_id'] = self.kwargs['id']

        return context


    def get_form_kwargs(self):
        kwargs = super(Alta_Datos, self).get_form_kwargs()
        kwargs['rfc'] = self.kwargs['rfc']
        return kwargs


    def form_valid(self, form):
        form.instance.usuario = self.request.user.username

        if User.objects.filter(username=self.request.user.username, groups__name__contains = 'VIGILANCIA').exists():
            form.instance.visible = False
        else:
            form.instance.visible = True

        return super(Alta_Datos, self).form_valid(form)


    def get_success_url(self):
        messages.info(self.request, 'contactos')

        # if self.kwargs['id'] == 0:
        #     return reverse_lazy('rec_app:lista-rec')
        # else:
        #     if User.objects.filter(username=self.request.user.username, groups__name__contains = 'VIGILANCIA').exists():
        #         return reverse_lazy('programacion_app:admin-programacion', kwargs={'id': self.kwargs['id'] })
        #     elif User.objects.filter(username=self.request.user.username, groups__name__contains = 'AUDITORIA').exists():
        #         return reverse_lazy('transferidos_app:admin-programacion-3', kwargs={'id': self.kwargs['id'] })
        #     else:
        #         return reverse_lazy('padrones_app:admin-programacion-2', kwargs={'id': self.kwargs['id'] })  

        return self.request.META['HTTP_REFERER'] 


class Ver_Contacto(LoginRequiredMixin, DetailView):
    model = REC
    template_name = 'rec/ver_contacto.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalles'] =  Contacto.objects.detalle_all_visible(self.kwargs.get('pk'))
        context['obligaciones'] =  Obligaciones.objects.filter(rfc=self.kwargs.get('pk'))

        return context  


class Editar_Datos(CRUDMixin, SuccessMessageMixin, UpdateView):
    permission_required = ('change_contacto')
    
    model = Contacto
    template_name = 'rec/editar_datos.html'
    form_class = ContactoForm
    success_message = 'Datos Actualizados!'
    
    def get_context_data(self, **kwargs):
        context = super(Editar_Datos, self).get_context_data(**kwargs)
        
        context['programa_id'] = self.kwargs['id']


        obj = self.get_object()

        if Codigos_Maestros.objects.filter(comentario=obj.puesto).exists():
            selected_puesto = Codigos_Maestros.objects.filter(comentario=obj.puesto)
            context['selected_puesto'] = selected_puesto[0].id
        else:
            context['selected_puesto'] = ''

        return context

    def get_form_kwargs(self):
        kwargs = super(Editar_Datos, self).get_form_kwargs()

        obj = Contacto.objects.filter(id=self.kwargs['pk'])
        #print(str(obj[0].rfc))
        kwargs['rfc'] = str(obj[0].rfc)

        #print('================')
        #print(kwargs['rfc'])

        return kwargs

    def form_valid(self, form):
        messages.info(self.request, 'contactos')
        
        form.instance.usuario = self.request.user.username

        if User.objects.filter(username=self.request.user.username, groups__name__contains = 'VIGILANCIA').exists():
            form.instance.visible = False
        else:
            form.instance.visible = True

        return super(Editar_Datos, self).form_valid(form)


    def get_success_url(self):
        if self.kwargs['id'] == 0:
            return reverse_lazy('rec_app:lista-rec')
        else:
            if User.objects.filter(username=self.request.user.username, groups__name__contains = 'VIGILANCIA').exists():
                return reverse_lazy('programacion_app:admin-programacion', kwargs={'id': self.kwargs['id'] })
            elif User.objects.filter(username=self.request.user.username, groups__name__contains = 'AUDITORIA').exists():
                return reverse_lazy('transferidos_app:admin-programacion-3', kwargs={'id': self.kwargs['id'] })
            else:
                return reverse_lazy('padrones_app:admin-programacion-2', kwargs={'id': self.kwargs['id'] })



class Resumen_Ejecutivo(LoginRequiredMixin, ListView):
    template_name = 'rec/resumen_ejecutivo.html'
    context_object_name = 'programacion'

    def get_queryset(self):
        rfc = self.kwargs.get('rfc').strip()
        
        if Programa.objects.filter(rfc = rfc).exists():
            queryset = Programa.objects.filter(rfc = rfc)[:1]
        elif Programa_Padrones.objects.filter(rfc = rfc).exists():
            queryset = Programa_Padrones.objects.filter(rfc = rfc)[:1]
        elif Programa_Transferidos.objects.filter(rfc = rfc).exists():
            queryset = Programa_Transferidos.objects.filter(rfc = rfc)[:1]
        elif REC.objects.filter(rfc=rfc).exists():
            queryset = REC.objects.filter(rfc=rfc)
        elif Cartas_Invitacion.objects.filter(rfc=rfc).exists():
            queryset = Cartas_Invitacion.objects.filter(rfc=rfc)
        else:
            queryset = None
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Resumen_Ejecutivo, self).get_context_data(**kwargs)

        rfc = self.kwargs.get('rfc').strip()
        list_programa = []
        list_padrones = []
        list_transferencias = []

        if Programa.objects.filter(rfc=rfc).exists():
            obj_Programa = Programa.objects.filter(rfc=rfc)
            
            for row in obj_Programa:
                list_programa.append(row.id)
            
            if REC.objects.filter(rfc=obj_Programa[0].rfc).exists():
                obj_REC = REC.objects.filter(rfc=obj_Programa[0].rfc)
                id_contacto = obj_REC[0].id
            else:
                id_contacto = 0
        else:
            id_contacto = 0
        
        
        if Programa_Padrones.objects.filter(rfc=rfc).exists():
            obj_Programa_Padrones = Programa_Padrones.objects.filter(rfc=rfc)
            
            for row in obj_Programa_Padrones:
                list_padrones.append(row.id)
            
            if REC.objects.filter(rfc=obj_Programa_Padrones[0].rfc).exists():
                obj_REC = REC.objects.filter(rfc=obj_Programa_Padrones[0].rfc)
                id_contacto = obj_REC[0].id
            else:
                id_contacto = 0
        else:
            id_contacto = 0
            
            
        if Programa_Transferidos.objects.filter(rfc=rfc).exists():
            obj_Programa_Transferidos = Programa_Transferidos.objects.filter(rfc=rfc)
            
            for row in obj_Programa_Transferidos:
                list_transferencias.append(row.id)
            
            if REC.objects.filter(rfc=obj_Programa_Transferidos[0].rfc).exists():
                obj_REC = REC.objects.filter(rfc=obj_Programa_Transferidos[0].rfc)
                id_contacto = obj_REC[0].id
            else:
                id_contacto = 0
        else:
            id_contacto = 0
            
            
        if REC.objects.filter(rfc=rfc).exists():
            obj_REC = REC.objects.filter(rfc=rfc)
            id_contacto = obj_REC[0].id
        else:
            id_contacto = 0
            
            
        context['archivos'] = Archivos.objects.select_related('programa_id').filter(programa_id__in = list_programa).order_by('-fecha')        
        context['archivos_padrones'] = Archivos_Padrones.objects.select_related('programa_id').filter(programa_id__in = list_padrones).order_by('-fecha')              

        context['pagos'] = Pagos.objects.select_related('programa_id').filter(programa_id__in = list_programa).order_by('-fecha')          
        context['pagos_padrones'] = Pagos_Padrones.objects.select_related('programa_id').filter(programa_id__in = list_padrones).order_by('-fecha')      

       
        mySql = f"""
            (select
                A.id,
                A.folio,	
                A.programa,	
                B.fecha,	
                A.presuntiva,	
                A.recaudado,	
                'VIGILANCIA Y CONTROL DE OBLIGACIONES' area,	
                A.estatus
            from programacion_programa A
                inner join programacion_detalle B
                    on A.id = B.programa_id_id
                where upper(A.rfc) = '{rfc.upper()}' and B.estatus = 'OFICIO' and A.folio <> '')
            union
            (select
                A.id,
                CASE
                    WHEN A.folio = '1' THEN cast(A.id as varchar)
                    ELSE
                        cast(A.folio as varchar)
                END folio,	
                A.programa,	
                A.fecha,	
                A.presuntiva,	
                A.recaudado,	
                A.area,	
                A.estatus
            from padrones_programa_padrones A
                where upper(A.rfc) = '{rfc.upper()}' and A.area = 'PADRONES' and A.is_active=true)
            union
            (select
                A.id,
                CASE
                    WHEN A.nuevo_folio = '' THEN cast(A.id as varchar)
                    ELSE
                        cast(A.nuevo_folio as varchar)
                END folio, 	
                A.programa,	
                A.fecha,	
                A.presuntiva,	
                A.recaudado,	
                A.area,	
                A.estatus
            from transferidos_programa_transferidos A
                where upper(A.rfc) = '{rfc.upper()}')
                order by fecha asc"""
                
        cursor = connection.cursor()          
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        queryset = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            queryset.append(dict(rowset))
            
        context['programas'] = queryset
        
        if not list_transferencias: 
            list_transferencias.append(0)
        if not list_padrones: 
            list_padrones.append(0)
        if not list_programa: 
            list_programa.append(0)
      
      
        
        mySql2 = f"""
            (select 
                B.folio,
                A.fecha,
                A.estatus, 
                A.comentarios,
                'VIGILANCIA Y CONTROL DE OBLIGACIONES' area
            from programacion_detalle A
                inner join programacion_programa B
                    on B.id = A.programa_id_id
                where A.programa_id_id in ({str(list_programa)[1:-1]})
                and A.estatus not in ('NUEVO','PROPUESTA','FAFD','PRESUNTIVA','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA'))
            union
            (select 
                CASE
                    WHEN B.folio = '1' THEN cast(B.id as varchar)
                    ELSE
                        cast(B.folio as varchar)
                END folio, 
                A.fecha,
                A.estatus, 
                A.comentarios,
                CASE
                    WHEN B.seguimiento = '' THEN 'PROGRAMACION'
                    ELSE
                        'PADRONES'
                END area
            from padrones_detalle_padrones A
                inner join padrones_programa_padrones B
                    on B.id = A.programa_id_id
                where A.programa_id_id in ({str(list_padrones)[1:-1]}))
            union
            (select 
                CASE
                    WHEN B.nuevo_folio = '' THEN cast(B.id as varchar)
                    ELSE
                        cast(B.nuevo_folio as varchar)
                END folio, 
                A.fecha,
                A.estatus, 
                A.comentarios,
                B.area
            from transferidos_detalle_transferidos A
                inner join transferidos_programa_transferidos B
                    on B.id = A.programa_id_id
                where A.programa_id_id in ({str(list_transferencias)[1:-1]}))
                order by fecha asc"""
        
        cursor2 = connection.cursor() 
        cursor2.execute(mySql2)
        fieldnames2 = [name[0] for name in cursor2.description]
        result2 = []
        for row in cursor2.fetchall():
            rowset = []
            for field in zip(fieldnames2, row):
                rowset.append(field)
            result2.append(dict(rowset))
            
        context['detalles'] = result2

        mySql3 = f"""select
                        A.id,
                        CASE
                            WHEN A.folio = '1' THEN cast(A.id as varchar)
                            ELSE
                                cast(A.folio as varchar)
                        END folio,	
                        A.programa,	
                        A.fecha,	
                        A.presuntiva,	
                        A.recaudado,	
                        A.area,	
                        A.estatus
                    from padrones_programa_padrones A
                        where upper(A.rfc) = '{rfc.upper()}' 
                        and A.area <> 'PADRONES'
                    order by fecha asc"""
                
        cursor3 = connection.cursor()          
        cursor3.execute(mySql3)
        fieldnames3 = [name[0] for name in cursor3.description]
        queryset3 = []
        for row in cursor3.fetchall():
            rowset = []
            for field in zip(fieldnames3, row):
                rowset.append(field)
            queryset3.append(dict(rowset))
            
        context['programas_masivo'] = queryset3
        
        context['contactos'] =  Contacto.objects.detalle_all(id_contacto)
        context['obligaciones'] =  Obligaciones.objects.filter(rfc=id_contacto)
        context['cartas_invitacion'] = Cartas_Invitacion.objects.filter(rfc=rfc)

        return context 
        
        
class Eliminar_Datos(CRUDMixin, DeleteView):
    permission_required = ('delete_contacto')
    
    model = Contacto
    template_name = 'rec/eliminar_datos.html'

    def delete(self, request, *args, **kwargs):
        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            obj_contacto = self.get_object()
            obj_contacto.is_active=False
            obj_contacto.save()

            message = 'Contacto Eliminado!'
            error = 'No hay error!'
            response = JsonResponse({'message': message, 'error': error})
            return response
        else:
            return reverse_lazy('rec_app:lista-rec')
    
    def get_success_url(self):
        return self.request.META['HTTP_REFERER']
            

class Get_Fiscalizados(ListView):
    model = Fiscalizados
    template_name = 'programacion/consulta/ver_contribuyente.html'

    def get_queryset(self):
        return Fiscalizados.objects.filter(rfc__icontains=self.kwargs.get('rfc'))


    def get(self, request, *args, **kwargs):

        #if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = serialize('json', self.get_queryset())
            
            return HttpResponse(data, 'application/json')
        else:
            return render(request, self.template_name)



class Get_Contribuyente(ListView):

    def get_data(self, rfc, opcion):

        url = "http://172.31.113.187:180/Informacion_Contribuyente.asmx?op=Obtiene_Informacion"
        headers = {
            'Content-Type': 'text/xml',
            'SOAPAction': 'http://tempuri.org/Obtiene_Informacion'
        }
        xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n  <soap:Body>\r\n    <Obtiene_Informacion xmlns=\"http://tempuri.org/\">\r\n      <rfc>" + \
            rfc + "</rfc>\r\n      <opcion>" + \
            str(opcion) + "</opcion>\r\n    </Obtiene_Informacion>\r\n  </soap:Body>\r\n</soap:Envelope>"

        response = requests.post(url, headers=headers, data=xml)
        dictionary = xmltodict.parse(response.text)

        for key, value in dictionary.items():
            for key2, value2 in value.items():
                if key2 == 'soap:Body':
                    for key3, value3 in value2.items():
                        if key3 == 'Obtiene_InformacionResponse':
                            for key4, value4 in value3.items():
                                if key4 == 'Obtiene_InformacionResult':
                                    result = json.loads(value4)

        return result['Table']

    def get(self, request, *args, **kwargs):

        rfc = self.kwargs.get('rfc')
        data = []

        # Consultas a SQL Server para informacion del contribuyente
        try:
            # Opcion 1 - Datos Generales SAT
            datos_sat = self.get_data(rfc, 1)
        except:
            datos_sat = []

        if datos_sat is None:
            try:
                # Opcion 2 - Datos Generales REC
                datos_rec = self.get_data(rfc, 2)
            except:
                datos_rec = []

            data = list(datos_rec)
        else:
            data = list(datos_sat)

        return JsonResponse(data, safe=False)

  
class Expediente(LoginRequiredMixin, TemplateView):
    template_name = 'rec/expediente.html'

    def get_context_data(self, **kwargs):
        context = super(Expediente, self).get_context_data(**kwargs)

        #context['total_registros'] = REC.objects.all().count()

        return context


class rec_notificados(ListAPIView):
    serializer_class = REC_Serializer

    def get_queryset(self):
        kword = self.kwargs['kword']

        queryset = REC_Notificados.objects.filter(
            Q(rfc__icontains = kword) | Q(nombre__icontains = kword)
        ).order_by('rfc')

        return queryset[:100]       


class Circulo_Credito_View(TemplateView):
    template_name = 'rec/circulo_credito.html'
    
    
    def get_context_data(self, **kwargs):
        context = super(Circulo_Credito_View, self).get_context_data(**kwargs)
        context['circulo_credito'] = Circulo_Credito.objects.filter(
            is_active=True
        )

        return context


# class Paginar(ListView):
#     template_name = 'rec/circulo_credito.html'
#     model = Circulo_Credito 
#     paginate_by = 5
#     context_object_name = 'paginar'

#     def get_context_data(self, **kwargs):
#         context = super(Circulo_Credito_View, self).get_context_data(**kwargs)
#         context['circulo_credito'] = Circulo_Credito.objects.all()

#         return context
class BusquedaCirculoCredito(ListAPIView):
    serializer_class = Circulo_Credito_Serializer

    def get_queryset(self):
        kword = self.kwargs['kword']


        queryset = Circulo_Credito.objects.filter(
            Q(rfc__icontains = kword) | Q(nombre__icontains = kword) | Q(numero_cuenta__icontains = kword),
            is_active=True
        ).order_by('-numero_cuenta')

        return queryset[:100]


class ReporteCirculoCreditoView(TemplateView):
    template_name = 'rec/reporte_circulo_credito.html'

    # def get_context_data(self, **kwargs):
    #     context = super(ReporteCirculoCreditoView, self).get_context_data(**kwargs)

    #     today = datetime.date.today()
    #     year = today.year

    #     context["ejercicio"] = year

    #     months = [
    #         "Enero",
    #         "Febrero",
    #         "Marzo",
    #         "Abril",
    #         "Mayo",
    #         "Junio",
    #         "Julio",
    #         "Agosto",
    #         "Septiembre",
    #         "Octubre",
    #         "Noviembre",
    #         "Diciembre"
    #     ]

    #     month = today.month
    #     periodos = []
    #     ini_month = 1
    #     for line in months:
    #         if ini_month <= month:
    #             periodo = {"item": "", "value": 0}
    #             periodo["value"] = ini_month
    #             periodo["item"] = line

    #             periodos.append(periodo)
    #         else:
    #             break

    #         ini_month += 1

    #     context['periodos'] = periodos
    #     return context


def DescargarExcelReporteCirculo(request):
    formData = request.POST

    filter_ejercicio = formData["anio"]
    filter_periodo = formData["periodo"]
    filter_tipo_persona = formData["tipo_persona"]
    
    cursor = connection.cursor()

    if filter_tipo_persona == "F":
        sql = f"SELECT * FROM reporte_circulo_fisicas({filter_periodo}, {filter_ejercicio})"
    else:
        sql = f"SELECT * FROM reporte_circulo_fisicas({filter_periodo}, {filter_ejercicio})"


    cursor.execute(sql)

    circulo = []
    for row in cursor.fetchall():
        rowset = []
        
        for field in row:
            rowset.append(field)
        circulo.append(rowset)

    header = [name[0] for name in cursor.description]
    
    # Create record of download of file
    # user_instance = User.objects.get(pk=request.user.id)
    # ejercicio = str(formData["anio"])

    # month_dict = {
    #     "1":'enero',
    #     "2":'febrero',
    #     "3":'marzo',
    #     "4":'abril',
    #     "5":'mayo',
    #     "6":'junio',
    #     "7":'julio',
    #     "8":'agosto',
    #     "9":'septiembre',
    #     "10":'octubre',
    #     "11":'noviembre',
    #     "12":'diciembre'
    # }
    
    # periodo = month_dict[str(formData["periodo"])]
    # full_name_user = str(user_instance.nombres) + " " + str(user_instance.apellidos) 

    # action = "El usuario " + full_name_user + " creó el reporte de círculo de crédito del ejercicio " + ejercicio + " y periodo de " + periodo

    # Historial_Reporte_Circulo_Credito.objects.create(
    #     accion = action,
    #     periodo = formData["periodo"],
    #     ejercicio = formData["anio"],
    #     usuario = user_instance
    # ).save()

    return generar_excel_orm(request, "reporte_circulo_credito.csv", circulo, header)


class Batch_Credito(TemplateView):
    template_name = 'rec/batch_credito.html'

    def get_context_data(self, **kwargs):
        context = super(Batch_Credito, self).get_context_data(**kwargs)
        context['Formulario'] = BatchForm
        
        return context

    def post(self, request, *args, **kwargs):
        path = settings.MEDIA_ROOT + '/batch/' + request.FILES['archivo'].name
        # path_resp = settings.MEDIA_ROOT + '/batch/'+ request.FILES['archivo'].name[:-4] + '_resp.csv'

        def handle_uploaded_file(file):
            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        def execute_batch_new(file):
            user = self.request.user.username
            area = self.request.user.unidad.nombre

            # Ejecutar Funcion
            cursor = connection.cursor()
            sql = f''' SELECT carga_circulo_credito('{file}','{user}','{area}'); '''
            cursor.execute(sql)
            resultado = cursor.fetchone()

            # mensage
            if resultado[0].split(':')[1] == 'ERROR':
                # archivo respuesta
                messages.info(self.request, resultado[0].split(':')[0])
                messages.error(self.request, 'Se generaron algunos errores, favor de revisar los datos que no se cargaron.')
            else:
                messages.success(self.request, 'Todos los datos se cargaron correctamente.')
            
        if request.method == 'POST':
            form = BatchForm(request.POST, request.FILES)

            if form.is_valid():   
                handle_uploaded_file(request.FILES['archivo']) 

                execute_batch_new(request.FILES['archivo'])

                return redirect(self.request.META['HTTP_REFERER'])

        else:
            form = BatchForm()

def DescargarExcel_Credito(request, archivo):
    path = 'C:/batch/ejecucion/' + archivo

    with open(path, 'rb') as file:
        response = HttpResponse(file.read(),content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)

    return response


class VerModal(DetailView):
    template_name = 'rec/ver_modal.html'
    model = Circulo_Credito
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(VerModal, self).get_context_data(**kwargs)
        contribuyente = self.get_object()

        context['historial'] = Circulo_Credito.objects.filter(
            rfc=contribuyente.rfc,
            numero_cuenta=contribuyente.numero_cuenta,
            is_active=False
        ).order_by('-id')
        
        return context


class Modal_Sintesis(DetailView):
    template_name = 'rec/modal-sintesis.html'
    model = Circulo_Credito
    context_object_name = 'sintesis'


class ServicioContribuyente(TemplateView):
    template_name = 'rec/servicios-contribuyente.html'
    
    def get_context_data(self, **kwargs):
        context = super(ServicioContribuyente, self).get_context_data(**kwargs)

        palabra_clave = self.request.GET.get('contribuyente','')
        if palabra_clave:
            lista = Circulo_Credito.objects.filter(
                Q(rfc__icontains = palabra_clave) | 
                Q(nombre__icontains = palabra_clave) |
                Q(numero_cuenta__icontains = palabra_clave),
                is_active=True
            )
        else:
            lista = []            
        
        context['contribuyente'] = lista

        return context


class Ver_Creditos(LoginRequiredMixin, TemplateView):
    template_name = 'rec/ver_creditos.html'

    def get_context_data(self, **kwargs):
        context = super(Ver_Creditos, self).get_context_data(**kwargs)


        palabra_clave = self.request.GET.get('rfc','')

        if palabra_clave:
            lista = Circulo_Credito.objects.filter(
                rfc__icontains=palabra_clave,
                is_active=True
            )
        else:
            lista = []

        return context

def DataCirculo(request):
    formData = request.POST

    palabra_clave = formData['kword']
    if palabra_clave:
        lista = Circulo_Credito.objects.filter(Q(rfc__icontains = palabra_clave) | Q(numero_cuenta__icontains = palabra_clave))
    else:
        lista = []  
                  
    return JsonResponse({'data': lista })
