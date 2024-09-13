import csv
from datetime import date

from django.http import HttpResponse
from django.db.models import Q, OuterRef, Subquery
from applications.programacion.models import Programa
from applications.users.models import User
from django.db import connection

def General_Excel_ORM(request, nombre_archivo, header, query):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + nombre_archivo

    writer = csv.writer(response)
    writer.writerow(header)

    for row in query:
        writer.writerow(row)

    return response

# Funciones para generar reportes en csv padrones
def padrones(request):
    FormData = request.GET

    nombre_archivo = 'Padrones_Asignacion ' + str(date.today()) + '.csv'
    header = ['id', 'oficio', 'rfc', 'nombre', 'programa', 'etapa', 'estatus', 'presuntiva', 'recaudado', 'fecha', 'ultimo_movimiento',
      'dias_sin_acciones', 'dias_seguimiento', 'color', 'fecha_notificacion', 'notificado', 'seguimiento', 'ministro', 'area']

    username = request.user.username
    user = request.user.nombres + ' ' + request.user.apellidos
    cursor = connection.cursor()

    sql = f'''
            SELECT 
                *
            FROM 
                padrones_seguimiento 
            WHERE 
                area ILIKE '%PADRONES%'
                and activo = true
            ORDER BY 
                dias_sin_acciones DESC
            ;'''
    
    cursor.execute(sql)
    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        for field in zip(fieldnames, row):
            rowset.append(field[1])
        result.append(list(rowset))        
    query = result
               
    return General_Excel_ORM(request,nombre_archivo,header,query)

