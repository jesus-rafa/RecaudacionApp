import csv

from datetime import date
from django.http import HttpResponse
from django.db.models import Q, OuterRef, Subquery
from applications.programacion.models import Programa
from django.db import connection
from applications.programacion.models import Programa
from applications.rec.models import Fiscalizados

def General_Excel_ORM(request, nombre_archivo, header, query):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + nombre_archivo

    writer = csv.writer(response)
    writer.writerow(header)

    for row in query:
        writer.writerow(row)

    return response

# Funciones para generar reportes en csv fiscalizados
def informativas(request):

    nombre_archivo = 'fiscalizados-informativas ' + str(date.today()) + '.csv'
    header = ['id','rfc','programa','presuntiva','nombre','direccion','fecha','estatus','seguimiento','usuario','dias','folio','recaudado','etapa','interlocutor','created','modified','is_close']

    query = Programa.objects.filter(estatus = 'INFORMATIVAS'
    ).distinct('id'
    ).values_list(
        'id','rfc','programa','presuntiva','nombre','direccion','fecha','estatus','seguimiento','usuario','dias','folio','recaudado','etapa','interlocutor','created','modified','is_close'
    )
               
    return General_Excel_ORM(request,nombre_archivo,header,query)

# Funciones para generar reportes en csv fiscalizados
def fiscalizados(request):

    nombre_archivo = 'fiscalizados ' + str(date.today()) + '.csv'
    header = ['id','created','modified','rfc','fecha_alta','is_active','usuario']

    query = Fiscalizados.objects.all(
    ).values_list(
        'id','created','modified','rfc','fecha_alta','is_active','usuario'
    )        

    return General_Excel_ORM(request,nombre_archivo,header,query)

