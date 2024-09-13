import csv
from datetime import date

from django.http import HttpResponse
from django.db.models import Q, OuterRef, Subquery
from .models import Programa
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

# Funciones para generar reportes en csv
def concluidos_vigilancia(request):

    nombre_archivo = 'concluidos vigilancia ' + str(date.today()) + '.csv'
    header = ['Oficio','RFC','Nombre','Programa','Presuntiva','Recaudado','Fecha Creación','Fecha Conclusión','Seguimiento','Estatus']

    query = Programa.objects.filter(
        estatus='CONCLUIDO', 
        detalle_programa__estatus = 'CONCLUIDO'
        #detalle_programa__fecha__range=['2021-01-01', '2021-12-31']
    ).distinct('id'
    ).values_list(
        'folio','rfc','nombre','programa','presuntiva','recaudado','fecha','fecha','seguimiento','estatus'
    )
               
    return General_Excel_ORM(request,nombre_archivo,header,query)

# Funciones para generar reportes en csv
def ultimos_movimientos(request):


    nombre_archivo = 'ultimos movimientos ' + str(date.today()) + '.csv'
    header = ['movimiento', 'fecha', 'rfc', 'nombre', 'usuario', 'comentario', 'area']

    cursor = connection.cursor()
    cursor.execute("SELECT movimiento, fecha, rfc, nombre, usuario, comentario, area FROM public.Ultimos_Movimientos ORDER BY FECHA DESC LIMIT 1000")
    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        for field in zip(fieldnames, row):
            rowset.append(field[1])
        result.append(list(rowset))

    query = result
               
    return General_Excel_ORM(request,nombre_archivo,header,query)