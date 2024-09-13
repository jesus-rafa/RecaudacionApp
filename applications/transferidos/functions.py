
import csv
from datetime import date

from django.http import HttpResponse
from django.db.models import Q, OuterRef, Subquery
from .models import Detalle_Transferidos, Programa_Transferidos

def General_Excel_ORM(request, nombre_archivo, header, query):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + nombre_archivo

    writer = csv.writer(response)
    writer.writerow(header)

    for row in query:
        writer.writerow(row)

    return response


# Funciones para generar reportes en csv
def activos_auditoria(request):

    nombre_archivo = 'activos auditoria ' + str(date.today()) + '.csv'
    header = ['origen','rfc','nombre','programa','fecha','metodo_envio','estatus','estatus_cierre']

    estatus = Detalle_Transferidos.objects.filter(
        programa_id=OuterRef('pk'),
        estatus = 'CIERRE'
    ).order_by('-fecha')

    query = Programa_Transferidos.objects.filter(
        area = 'AUDITORIA',
        is_active = True,
        estatus__in = ['ACEPTADO', 'ACTIVO','CIERRE']
    ).annotate(
        estatus_cierre=Subquery(estatus.values('fecha')[:1])
    ).values_list(
        'estatus','rfc','nombre','programa','fecha','metodo_envio','estatus','estatus_cierre'
    )

    return General_Excel_ORM(request,nombre_archivo,header,query)

def activos_ejecucion(request):

    nombre_archivo = 'activos ejecucion ' + str(date.today()) + '.csv'
    header = ['origen','rfc','nombre','programa','fecha','metodo_envio','estatus','estatus_cierre']

    estatus = Detalle_Transferidos.objects.filter(
        programa_id=OuterRef('pk'),
        estatus = 'CIERRE'
    ).order_by('-fecha')

    query = Programa_Transferidos.objects.filter(
        area = 'EJECUCION',
        is_active = True,
        estatus__in = ['ACEPTADO', 'ACTIVO','CIERRE']
    ).annotate(
        estatus_cierre=Subquery(estatus.values('fecha')[:1])
    ).values_list(
        'estatus','rfc','nombre','programa','fecha','metodo_envio','estatus','estatus_cierre'
    )

    return General_Excel_ORM(request,nombre_archivo,header,query)
