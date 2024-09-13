import csv

from django.http import HttpResponse

from applications.users.models import User

def generar_excel_orm(request, nombre_archivo, body_file, header_file):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename=' + nombre_archivo
    
    writer = csv.writer(response)
    writer.writerow(header_file)

    if body_file:
        for row in body_file:
            writer.writerow(row)
    
    return response

def validar_permite_consultar_expediente(username):
    response = False
    if User.objects.filter(username=username, groups__name__in=['EXPEDIENTE']):
        response = True
    
    return response
