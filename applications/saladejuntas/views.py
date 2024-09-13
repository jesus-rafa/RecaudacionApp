from django.conf import settings
from django.shortcuts import render
from django.db.models.query import QuerySet
from django.db import connection
from django.http.response import JsonResponse
from django.core import serializers
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import (ListView, CreateView, UpdateView, DetailView, TemplateView)

from .models import Sala, Reuniones, Categoria, HistoricoReuniones, EstatusReuniones, ParticipantesReuniones, notificacionesCoffeBreak
from .functions import add_historico_reuniones, es_correo_valido, crear_evento, eliminar_evento, enviar_correo

from applications.users.models import User, Areas

import json
import os
import csv
import calendar
import pytz
import datetime
import pdfkit
import base64
import random
from datetime import datetime, date, timedelta

# path to your wkhtmltopdf.exe file
wkhtml_to_pdf = os.path.join(
    settings.BASE_DIR, "wkhtmltopdf.exe")


class SalasJuntasView(TemplateView):
    template_name = 'salajuntas/sala-juntas.html'

    def get_context_data(self, **kwargs):
        sala_get = self.request.GET.get("sala", '')

        context = super(SalasJuntasView, self).get_context_data(**kwargs)
        context['catalogos_salas'] = Sala.objects.filter(is_active=True).order_by('id')
        context['categorias'] = Categoria.objects.order_by('id')
        context['areas'] = Areas.objects.order_by('id')

        today = datetime.now()
        date_ini = str(today.year) + "-" + str(today.month) + "-" + "01"
        date_end = today.replace(day = calendar.monthrange(today.year, today.month)[1]).strftime("%Y-%m-%d")
        
        # notificacion_coffe_break_instance = Areas.objects.get(pk=self.request.user.area)
        # correo_noti = notificacion_coffe_break_instance.correo_notificacion_coffe_break
        # if notificacion_coffe_break_instance:
        #     for correo in notificacion_coffe_break_instance:
        #         correo_noti = correo.correo
        # correo_noti = self.request.user.area.correo_notificacion_coffe_break

        context["correo_notificacion"] = self.request.user.areas.correo_notificacion_coffe_break
        horarios = [
            {"value":"08:30", "hora": "08:30 a.m."},
            {"value":"09:00", "hora": "09:00 a.m."},
            {"value":"09:30", "hora": "09:30 a.m."},
            {"value":"10:00", "hora": "10:00 a.m."},
            {"value":"10:30", "hora": "10:30 a.m."},
            {"value":"11:00", "hora": "11:00 a.m."},
            {"value":"11:30", "hora": "11:30 a.m."},
            {"value":"12:00", "hora": "12:00 p.m."},
            {"value":"12:30", "hora": "12:30 p.m."},
            {"value":"13:00", "hora": "01:00 p.m."},
            {"value":"13:30", "hora": "01:30 p.m."},
            {"value":"14:00", "hora": "02:00 p.m."},
            {"value":"14:30", "hora": "02:30 p.m."},
            {"value":"15:00", "hora": "03:00 p.m."},
            {"value":"15:30", "hora": "03:30 p.m."},
            {"value":"16:00", "hora": "04:00 p.m."},
            {"value":"16:30", "hora": "04:30 p.m."},
            {"value":"17:00", "hora": "05:00 p.m."},
            {"value":"17:30", "hora": "05:30 p.m."},
            {"value":"18:00", "hora": "06:00 p.m."},
            {"value":"18:30", "hora": "06:30 p.m."},
            {"value":"19:00", "hora": "07:00 p.m."},
            {"value":"19:30", "hora": "07:30 p.m."},
            {"value":"20:00", "hora": "08:00 p.m."},
            {"value":"20:30", "hora": "08:30 p.m."},
            {"value":"21:00", "hora": "09:00 p.m."},
            {"value":"21:30", "hora": "09:30 p.m."},
            {"value":"22:00", "hora": "10:00 p.m."},
            {"value":"22:30", "hora": "10:30 p.m."},
            {"value":"23:00", "hora": "11:00 p.m."}
        ]

        z_mx = pytz.timezone('America/Mexico_City')
        tiempo = datetime.now()
        tiempo_horas = tiempo.strftime("%H")
        tiempo_minutos = tiempo.strftime("%M")

        horarios_disponibles = []
        for item in horarios:
            a_horarios = item["value"].split(':')
            if tiempo_horas <= a_horarios[0] and tiempo_minutos <= a_horarios[1]:
                obj_horario_disp = {"value": item["value"], "hora": item["hora"]}
                horarios_disponibles.append(obj_horario_disp)

        context["horas_disponibles"] = horarios

        sala_id = 1
        if sala_get:
            sala_id = sala_get

        sala_instance = Sala.objects.filter(pk=sala_id)
        if sala_instance:
            context['obj_sala_default'] = Sala.objects.get(pk=sala_id)

        context['sala_default'] = sala_id
        context['reuniones'] = Reuniones.objects.filter(sala=sala_id, fecha_reunion__lte=date_end, fecha_reunion__gte=date_ini, is_active=True)
        context['usuarios'] = User.objects.filter(is_active=True)

        context["accion_agregar"] = 0
        context["accion_eliminar"] = 0
        context["accion_cambiar_horario"] = 0
        if User.objects.filter(username=self.request.user.username, groups__name__in=['SALA DE JUNTAS DIRECTIVOS', 'SALA DE JUNTAS ASISTENTES']).exists():
            context["accion_agregar"] = 1
            context["accion_eliminar"] = 1
            context["accion_cambiar_horario"] = 1

        return context

def BuscarCorreoUsuario(request):
    FormData = request.POST

    correo_usuario = ""
    usuarios_instance = User.objects.filter(id=FormData["id_usuario"])
    if usuarios_instance:
        for usuario in usuarios_instance:
            correo_usuario = usuario.email

    return JsonResponse({'error': False, "data": correo_usuario, 'msj': "" })

def BuscarCorreoNotificacion(request):
    FormData = request.POST

    usuario_responsable_reunion_id = FormData['usuario_responsable_id']

    responsable_reunion = User.objects.get(pk=usuario_responsable_reunion_id)
    correo_noti = ""
    if responsable_reunion:
        correo_noti = responsable_reunion.areas.correo_notificacion_coffe_break

    return JsonResponse({'error': False, "correo_notificacion": correo_noti, 'msj': "" })

def EliminarReuniones(request):
    FormData = request.POST

    reunion_id = FormData['id_evento']

    if not reunion_id:
        return JsonResponse({'error': True, 'data': reunion_id, 'msj': "Problemas a procesar la solicitud consulte con el administrador del sistema" })

    reunion_instance = Reuniones.objects.get(pk=reunion_id)
    # correo para el usuario notificación
    usuario_notificaciones = reunion_instance.usuario_responsable.areas.correo_notificacion_coffe_break
    # Validar si el usuario con sesión creo la reunión
    if reunion_instance.usuario.id != request.user.id:
        if not User.objects.filter(username=request.user.username, groups__name__in=['SALA DE JUNTAS DIRECTIVOS']).exists():
            return JsonResponse({'error': True, 'msj': "No tiene los permisos para eliminar reuniones que no fueron creadas por su usuario" })

    reunion_instance.is_active = False
    reunion_instance.save()

    sala_instance = Sala.objects.get(pk=FormData['filter-salas'])

    user_instance = User.objects.get(pk=request.user.id)
    estatus_instance = EstatusReuniones.objects.get(pk=2)
    full_name_user = str(user_instance.nombres) + " " + str(user_instance.apellidos)
    fecha_reunion = datetime.strptime(str(reunion_instance.fecha_reunion), "%Y-%m-%d")
    accion = "El usuario " + full_name_user + " canceló la reunión : '" + str(reunion_instance.evento) + "' de la fecha " + fecha_reunion.strftime("%d/%m/%Y") + "."

    add_historico_reuniones(request, reunion_instance, user_instance, estatus_instance, accion)

    # Eliminar reuniones de calendario
    if reunion_instance.evento_id:
        calendar_id = str(sala_instance.calendario_id)
        eliminar_evento(calendar_id, str(reunion_instance.evento_id))
    
    # Enviar notificación a la persona encargada del coffe break
    if usuario_notificaciones:
        if reunion_instance.requiere_coffe_break:
            hora_fin_reunion = str(reunion_instance.hora_fin_reunion)
            hora_inicio_reunion = str(reunion_instance.hora_ini_reunion)
            # titulo_contenido_correo = "Reunión para el día " + fecha_reunion.strftime("%d/%m/%Y") + " de " + hora_inicio_reunion + " a " + hora_fin_reunion + " hrs."
            titulo_contenido_correo = False # Este campo ya no se usa
            correo_para = usuario_notificaciones
            correo_asunto = "Se cancela reunión del día " + fecha_reunion.strftime("%d/%m/%Y") + " en " + str(sala_instance.descripcion) + " de " + hora_inicio_reunion + " - " + hora_fin_reunion + " hrs."
            contenido_html = """\
            <html>
            <body style="font-family: Arial, Helvetica, sans-serif;">
                <h3><b>Evento cancelado</b> en """ + str(sala_instance.descripcion) + """ el día """ + fecha_reunion.strftime("%d/%m/%Y") + """ de """ + hora_inicio_reunion + """ a """ + hora_fin_reunion + """ hrs.</h3>
                <h5>Detalles del Coffe Break:</h5>
                <p><strike>""" + str(reunion_instance.detalles_coffe_break) + """</strike></p>
                <br>
                <p style="font: small/1.5 Arial,Helvetica,sans-serif; color:gray;">
                --<br> 
                SERVICIO DE ADMINISTRACIÓN TRIBUTARIA DEL ESTADO DE GUANAJUATO<br>
                Plaza de la Paz No. 100, Puerto Interior. Silao de la Victoria, Gto. C.P. 36275 Tel. 4773433300 
                </p>
                <br>
                <b>Nota: Favor de no responder a esta dirección de correo electrónico.</b>
            </body>
            </html>
            """
            enviar_correo(correo_asunto, correo_para, contenido_html, titulo_contenido_correo)

    return JsonResponse({'error': False, 'data': [], 'msj': "Registro eliminado correctamente" })

def ConsultaReunionesBySala(request):
    FormData = request.POST

    sala_id = FormData['filter-salas']
    mes_ini = FormData['filter-mes_ini']
    mes_fin = FormData['filter-mes_fin']
    anyo_ini = FormData['filter-anyo_ini']
    anyo_fin = FormData['filter-anyo_fin']

    fecha_ini = str(anyo_ini)+ "-" + str(mes_ini) + "-01"

    if mes_ini == mes_fin:
        calendar_period = calendar.monthrange(int(anyo_ini), int(mes_ini))
        day = calendar_period[1]
        fecha_fin = str(anyo_ini) + "-" + str(mes_ini) + "-" + str(day)
    else:
        calendar_period = calendar.monthrange(int(anyo_fin), int(mes_fin))
        day = calendar_period[1]
        fecha_fin = str(anyo_fin) + "-" + str(mes_fin) + "-" + str(day)

    if not sala_id:
        return JsonResponse({'error': True, 'data': sala_id, 'msj': "Problemas a procesar la solicitud consulte con el administrador del sistema" })

    cursor = connection.cursor()
    sql = f'''
        SELECT reuniones.evento, reuniones.hora_ini_reunion, reuniones.hora_fin_reunion, reuniones.fecha_reunion, sc.color as color_categoria, reuniones.id, ss.capacidad_sala
        FROM saladejuntas_reuniones reuniones
        INNER JOIN saladejuntas_categoria sc ON sc.id = reuniones.categoria_id
        INNER JOIN saladejuntas_sala ss ON ss.id = reuniones.sala_id
        WHERE reuniones.sala_id = {sala_id} AND reuniones.is_active = TRUE AND reuniones.fecha_reunion >= '{fecha_ini}' AND reuniones.fecha_reunion <= '{fecha_fin}';
    '''
    cursor.execute(sql)

    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        for field in zip(fieldnames, row):
            rowset.append(field)
        result.append(dict(rowset))
    
    capacidad_sala = list(Sala.objects.filter(pk=sala_id).values('capacidad_sala'))

    return JsonResponse({'error': False, 'data': result, "sala": capacidad_sala, 'msj': "Calendario actualizado correctamente" })

def BuscarReuniones(request):
    FormData = request.POST

    evento_id = FormData['id_evento']

    if not evento_id:
        return JsonResponse({'error': True, 'data': sala_id, 'msj': "Problemas a procesar la solicitud consulte con el administrador del sistema" })

    if "cambiar_horario" in FormData:
        reunion_instance = Reuniones.objects.get(pk=evento_id)
        if reunion_instance.usuario.id != request.user.id:
            if not User.objects.filter(username=request.user.username, groups__name__in=['SALA DE JUNTAS DIRECTIVOS']).exists():
                return JsonResponse({'error': True, 'msj': "No tiene los permisos necesarios para cambiar de horario reuniones que no fueron creadas por su usuario" })

    cursor = connection.cursor() 
    sql = f'''
        SELECT reuniones.evento, reuniones.responsable_reunion, reuniones.hora_ini_reunion, reuniones.hora_fin_reunion, TO_CHAR(reuniones.fecha_reunion::date, 'dd/mm/yyyy') as fecha_reunion, reuniones.fecha_reunion as fecha_reunion_formato, sc.descripcion as categoria, reuniones.tiempo_coffe_break, reuniones.requiere_coffe_break, ua.nombre as area,
        reuniones.descripcion_evento, reuniones.total_participantes, reuniones.detalles_coffe_break, reuniones.categoria_id, reuniones.usuario_responsable_id, ss.descripcion as sala_descripcion
        FROM saladejuntas_reuniones reuniones
        LEFT JOIN saladejuntas_categoria sc ON sc.id = reuniones.categoria_id
        LEFT JOIN users_areas ua ON ua.id = reuniones.area_id
        LEFT JOIN users_user uu ON uu.id = reuniones.usuario_responsable_id
        LEFT JOIN saladejuntas_sala ss ON ss.id = reuniones.sala_id
        WHERE reuniones.id = {evento_id} AND reuniones.is_active = TRUE;
    '''
    cursor.execute(sql)

    fieldnames = [name[0] for name in cursor.description]  
    result = []
    for row in cursor.fetchall():
        rowset = []
        for field in zip(fieldnames, row):
            rowset.append(field)
        result.append(dict(rowset))
    
    vista_lista_participantes = True
    reunion_instance = Reuniones.objects.get(pk=evento_id)
    if reunion_instance.usuario.id != request.user.id:

        vista_lista_participantes = False
        if User.objects.filter(username=request.user.username, groups__name__in=['SALA DE JUNTAS DIRECTIVOS']).exists():
            vista_lista_participantes = True
    
    participantes = list(ParticipantesReuniones.objects.filter(reunion_sala_de_juntas=evento_id, is_active=True).values('nombre', 'correo'))

    return JsonResponse({'error': False, 'data': result[0], "listado_participantes" : participantes, "vista_listado_participantes": vista_lista_participantes, 'msj': "Evento Encontrado" })

def Crear_Reunion(request):
    FormData = request.POST
    # FormDataFiles = request.FILES

    correos_participantes = []

    for participantes in json.loads(FormData['listado_participantes']):
        # correos_participantes.append(participantes)
        # Validamos que el campo de correo no este vacío
        if participantes['correo']:
            # Validamos que el campo de correo tenga una estructura correcta
            if not es_correo_valido(participantes['correo']):
                return JsonResponse({'error': True, 'data': [], 'msj': "En el listado de participantes tiene un correo con formato incorrecto, participante: " +  str(row['nombre'])})

        # Agregamos a la lista los correos de los participantes
        correos_participantes.append({"nombre": participantes['nombre'], "correo": participantes['correo']})

    # Por si se recibe un archivo con el listado de salas de juntas
    # Se guardan el registro de cada asistente a la reunión
    # if FormDataFiles['archivo']:
    #     file = FormDataFiles['archivo']
        
    #     path = settings.MEDIA_ROOT + '/batch/' + file.name

    #     with open(path, 'wb+') as destination:
    #         for chunk in file.chunks():
    #             destination.write(chunk)

    #     with open(path, newline='') as csvfile:
    #         reader = csv.DictReader(csvfile)
    #         for row in reader:
    #             # Validamos que el campo de correo no este vacío
    #             if row['correo']:
    #                 # Validamos que el campo de correo tenga una estructura correcta
    #                 if not es_correo_valido(row['correo']):
    #                     return JsonResponse({'error': True, 'data': [], 'msj': "En el listado de participantes tiene un correo con formato incorrecto, participante: " +  str(row['nombre'])})

    #             # Agregamos a la lista los correos de los participantes
    #             correos_participantes.append({"nombre": row['nombre'], "correo": row['correo']})
    user_instance = User.objects.get(pk=request.user.id)
    responsable_reunion_instance = User.objects.get(pk=FormData['responsable_reunion'])
    categoria_instance = Categoria.objects.get(pk=FormData['categoria'])

    sala_instance = Sala.objects.get(pk=FormData['filter-salas'])
    # definimos el nombre de la sala anterior donde fue creada la reunión
    sala_anterior = str(sala_instance.descripcion)

    # definimos el nombre de la sala actual dejando la sala anterior como predefinida
    sala_actual = str(sala_instance.descripcion)
    sala_busqueda = FormData['filter-salas']
    if "slct_cambio_sala" in FormData:
        if FormData["slct_cambio_sala"] != "":
            cmb_sala_instance = Sala.objects.get(pk=FormData['slct_cambio_sala'])
            sala_actual = str(cmb_sala_instance.descripcion)
            sala_busqueda = FormData['slct_cambio_sala']

            # Validamos que la cantidad de participantes agregados al correo no exeda la capacidad máxima de personas por sala 
            if len(correos_participantes) > int(cmb_sala_instance.capacidad_sala):
                return JsonResponse({'error': True, 'data': [], 'msj': "El número de participantes del listado es mayor a la capacidad máxima de la sala (max. " + str(cmb_sala_instance.capacidad_sala) + ")"})

    area_responsable_reunion = responsable_reunion_instance.areas
    if not area_responsable_reunion:
        return JsonResponse({'error': True, 'data': [], 'msj': "El usuario que solicita la reunión no tiene un área relacionada en el sistema."})

    reuniones_dia = Reuniones.objects.filter(fecha_reunion=FormData['fecha_ini_reunion'], sala=sala_busqueda, is_active=True)
    area_instance = Areas.objects.get(pk=responsable_reunion_instance.areas.id)
    estatus_instance = EstatusReuniones.objects.get(pk=1)
    usuario_notificaciones_instance = notificacionesCoffeBreak.objects.get(is_active=True)
    usuario_responsable_reunion = str(responsable_reunion_instance.nombres) + " " + str(responsable_reunion_instance.apellidos)

    hora_inicio = str(FormData['hora_inicio']).split(':')
    hora_final = str(FormData['hora_final']).split(':')

    # Validamos que la cantidad de participantes agregradas en el campo de coffe break
    if int(FormData['total_participantes']) > int(sala_instance.capacidad_sala):
        return JsonResponse({'error': True, 'data': [], 'msj': "El total de participantes ingresados es mayor a la capacidad máxima de la sala"})

    # Validamos que la cantidad de participantes agregados al correo no exeda la capacidad máxima de personas por sala 
    if len(correos_participantes) > int(sala_instance.capacidad_sala):
        return JsonResponse({'error': True, 'data': [], 'msj': "El número de participantes del listado es mayor a la capacidad máxima de la sala"})

    # Calculamos el total de minutos
    total_minutos = ((int(hora_final[0]) - int(hora_inicio[0])) * 60 ) + (int(hora_final[1]) - int(hora_inicio[1]))

    requiere_coffe_break = False
    if 'requiere_coffe_break' in FormData:
        if FormData['requiere_coffe_break'] == "on":
            requiere_coffe_break = True

    str_fecha_hora_ini_reunion =  str(FormData['fecha_ini_reunion']) + " " + str(FormData['hora_inicio']) + ":00"
    fecha_hora_ini_reunion = datetime.strptime(str_fecha_hora_ini_reunion, "%Y-%m-%d %H:%M:%S")

    str_fecha_hora_fin_reunion =  str(FormData['fecha_ini_reunion']) + " " + str(FormData['hora_final']) + ":00"
    fecha_hora_fin_reunion = datetime.strptime(str_fecha_hora_fin_reunion, "%Y-%m-%d %H:%M:%S")

    if reuniones_dia:
        for dia in reuniones_dia:
            if FormData["id_evento"] != "":
                if int(dia.id) != int(FormData["id_evento"]):
                    fecha_hora_ini_ocupado = datetime.strptime(str(dia.fecha_reunion) + " " + str(dia.hora_ini_reunion) + ":00", "%Y-%m-%d %H:%M:%S")
                    fecha_hora_fin_ocupado = datetime.strptime(str(dia.fecha_reunion) + " " + str(dia.hora_fin_reunion) + ":00", "%Y-%m-%d %H:%M:%S")

                    # Validar que no haya una reunión ya agendada en el horario marcado por el usuario
                    if fecha_hora_ini_reunion >= fecha_hora_ini_ocupado and fecha_hora_ini_reunion < fecha_hora_fin_ocupado:
                        return JsonResponse({'error': True, 'data': FormData, 'msj': "Ya existe una reunión agendada en el rango de horario ingresado" })

                    if fecha_hora_ini_reunion < fecha_hora_ini_ocupado:
                        # Validar que no haya una reunión ya agendada en el horario marcado por el usuario
                        if fecha_hora_fin_reunion > fecha_hora_ini_ocupado:
                            return JsonResponse({'error': True, 'data': FormData, 'msj': "Ya existe una reunión agendada en el rango de horario ingresado" })
            else:
                fecha_hora_ini_ocupado = datetime.strptime(str(dia.fecha_reunion) + " " + str(dia.hora_ini_reunion) + ":00", "%Y-%m-%d %H:%M:%S")
                fecha_hora_fin_ocupado = datetime.strptime(str(dia.fecha_reunion) + " " + str(dia.hora_fin_reunion) + ":00", "%Y-%m-%d %H:%M:%S")

                # Validar que no haya una reunión ya agendada en el horario marcado por el usuario
                if fecha_hora_ini_reunion >= fecha_hora_ini_ocupado and fecha_hora_ini_reunion < fecha_hora_fin_ocupado:
                    return JsonResponse({'error': True, 'data': FormData, 'msj': "Ya existe una reunión agendada en el rango de horario ingresado" })
                
                if fecha_hora_ini_reunion < fecha_hora_ini_ocupado:
                    # Validar que no haya una reunión ya agendada en el horario marcado por el usuario
                    if fecha_hora_fin_reunion > fecha_hora_ini_ocupado:
                        return JsonResponse({'error': True, 'data': FormData, 'msj': "Ya existe una reunión agendada en el rango de horario ingresado" })

    if FormData["id_evento"] != "":
        # Reunion actual
        reunion = FormData['id_evento']

        sala_instance = Sala.objects.get(pk=FormData['slct_cambio_sala'])

        # Se asigna el estatus 3 de reunión re agendada
        estatus_instance = EstatusReuniones.objects.get(pk=3)

        reunion_instance = Reuniones.objects.get(pk=FormData['id_evento'])
        reunion_instance.evento = FormData['event-title']
        reunion_instance.descripcion_evento = FormData['descripcion_evento']
        reunion_instance.categoria = categoria_instance
        reunion_instance.sala = sala_instance
        reunion_instance.area = area_instance
        reunion_instance.fecha_reunion = FormData['fecha_ini_reunion']
        reunion_instance.hora_ini_reunion = FormData['hora_inicio']
        reunion_instance.hora_fin_reunion = FormData['hora_final']
        reunion_instance.usuario = user_instance
        reunion_instance.tiempo = total_minutos
        reunion_instance.requiere_coffe_break = requiere_coffe_break
        reunion_instance.detalles_coffe_break = FormData['detalles_coffe_break']
        reunion_instance.estatus = estatus_instance
        reunion_instance.responsable_reunion = usuario_responsable_reunion
        reunion_instance.total_participantes = FormData['total_participantes']
        reunion_instance.usuario_noti_coffe_break = usuario_notificaciones_instance
        reunion_instance.usuario_responsable = responsable_reunion_instance
        reunion_instance.save()

        # update participantes
        ParticipantesReuniones.objects.filter(reunion_sala_de_juntas=reunion, is_active=True).update(is_active=False)
    else:
        reunion = Reuniones.objects.create(
                evento = FormData['event-title'], 
                descripcion_evento = FormData['descripcion_evento'],
                categoria = categoria_instance, 
                sala = sala_instance, 
                area = area_instance,
                fecha_reunion = FormData['fecha_ini_reunion'],
                hora_ini_reunion = FormData['hora_inicio'],
                hora_fin_reunion = FormData['hora_final'],
                usuario = user_instance,
                tiempo = total_minutos,
                requiere_coffe_break = requiere_coffe_break,
                # tiempo_coffe_break = FormData['tiempo_coffe_break'],
                detalles_coffe_break = FormData['detalles_coffe_break'],
                estatus = estatus_instance,
                responsable_reunion = usuario_responsable_reunion,
                total_participantes = FormData['total_participantes'],
                usuario_noti_coffe_break = usuario_notificaciones_instance,
                usuario_responsable = responsable_reunion_instance
            ).pk

    if reunion:
        # get instance de la tabla Reuniones
        reunion_instance = Reuniones.objects.get(pk=reunion)


        full_name_user = str(user_instance.nombres) + " " + str(user_instance.apellidos) 
        descripcion_sala = str(sala_instance.descripcion)
        fecha_reunion = datetime.strptime(str(FormData['fecha_ini_reunion']), "%Y-%m-%d")
        if FormData["id_evento"] != "":
            if sala_actual == sala_anterior:
                accion = "El usuario " + full_name_user +" cambio de horario la reunión para la sala '" + descripcion_sala + "' en la fecha del " + fecha_reunion.strftime("%d/%m/%Y") + " con el horario de "+ str(FormData['hora_inicio']) + " a " + str(FormData['hora_final']) + " hrs."
            else:
                accion = "El usuario " + full_name_user +" cambio de sala de reunión pasando de la sala '" + sala_anterior + "' a la sala '" + sala_actual + "' en la fecha del " + fecha_reunion.strftime("%d/%m/%Y") + " con el horario de "+ str(FormData['hora_inicio']) + " a " + str(FormData['hora_final']) + " hrs."
        else:
            accion = "El usuario " + full_name_user +" agendó una reunión en la sala '" + descripcion_sala + "' para la fecha del " + fecha_reunion.strftime("%d/%m/%Y") + " con el horario de "+ str(FormData['hora_inicio']) + " a " + str(FormData['hora_final']) + " hrs."
        
        # Agregar el historial de la agenda de reunión
        add_historico_reuniones(request, reunion_instance, user_instance, estatus_instance, accion)

        # Se guardan el registro de cada asistente a la reunión
        if len(correos_participantes) > 0:
            
            for participante in correos_participantes:
                # Agregar los participantes a la sala de juntas
                ParticipantesReuniones.objects.create(
                    reunion_sala_de_juntas = reunion_instance, 
                    correo = participante['correo'], 
                    nombre = participante['nombre']
                ).save()

        # Agregar la validación para el envío del correo
        if len(correos_participantes) > 0:
            # Si existía una reunión eliminar la reunión anterior
            if FormData["id_evento"] != "":
                sala_instance_anterior = Sala.objects.get(pk=FormData['filter-salas'])
                calendar_id = str(sala_instance_anterior.calendario_id)
                # Eliminar la reunión ya generada
                eliminar_evento(calendar_id, str(reunion_instance.evento_id))
            
            categoria_descripcion = str(categoria_instance.descripcion)
            descripcion_evento = str(reunion_instance.descripcion_evento)
            # descripcion_evento = "Se reservó " + descripcion_sala + " para " + categoria_descripcion + " en las oficinas de Servicio de Administración Tributaria del Estado de Guanajuato"
            hora_inicio_reunion = str(reunion_instance.hora_ini_reunion) + ":00"
            hora_fin_reunion = str(reunion_instance.hora_fin_reunion) + ":00"

            horario_inicial_reunion = fecha_reunion.strftime("%Y-%m-%d") + " " + hora_inicio_reunion
            horario_final_reunion = fecha_reunion.strftime("%Y-%m-%d") + " " + hora_fin_reunion

            participantes_correos = []
            for correo in correos_participantes:
                if correo['correo']:
                    participantes_correos.append({'email': correo['correo']})

            if sala_instance.calendario_id:
                evento_id = crear_evento(FormData['event-title'], descripcion_evento, horario_inicial_reunion, horario_final_reunion, str(sala_instance.calendario_id), participantes_correos)

                # get instance de la tabla Reuniones
                reuniones_instance = Reuniones.objects.get(pk=reunion)
                reuniones_instance.evento_id = evento_id
                reuniones_instance.save()

        # Validar si necesita coffe break la reunión
        if requiere_coffe_break:
            usuario_notificaciones = responsable_reunion_instance.areas.correo_notificacion_coffe_break
            if usuario_notificaciones:
                # enviar correo a persona encargada del coffe break
                titulo_contenido_correo = "Reunión para el día " + fecha_reunion.strftime("%d/%m/%Y") + " de " + hora_inicio_reunion + " a " + hora_fin_reunion + " hrs."
                correo_para = usuario_notificaciones
                correo_asunto = "Se necesita Coffe Break para el día " + fecha_reunion.strftime("%d/%m/%Y") + " en " + str(sala_instance.descripcion) + " de " + hora_inicio_reunion + " - " + hora_fin_reunion + " hrs."
                contenido_html = """\
                <html>
                <body style="font-family: Arial, Helvetica, sans-serif;">
                    <h2>Reunión en """ + str(sala_instance.descripcion) + """ el día """ + fecha_reunion.strftime("%d/%m/%Y") + """ de """ + hora_inicio_reunion + """ a """ + hora_fin_reunion + """ hrs.</h2>
                    <h4>Detalles del Coffe Break:</h4>
                    <p>""" + str(reunion_instance.detalles_coffe_break) + """</p>  
                    <br>
                    <p style="font: small/1.5 Arial,Helvetica,sans-serif; color:gray;">
                    --<br> 
                    SERVICIO DE ADMINISTRACIÓN TRIBUTARIA DEL ESTADO DE GUANAJUATO<br>
                    Plaza de la Paz No. 100, Puerto Interior. Silao de la Victoria, Gto. C.P. 36275 Tel. 4773433300 
                    </p>
                    <br>
                    <b>Nota: Favor de no responder a esta dirección de correo electrónico.</b>
                </body>
                </html>
                """
                enviar_correo(correo_asunto, correo_para, contenido_html, titulo_contenido_correo)


        # pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

    return JsonResponse({'error': False, 'data': {'color_categoria': categoria_instance.color, "id": reunion_instance.id}, 'msj': "Reunión programada correctamente" })

def ListaAsistenciaReuniones(request, reunion):
    options = {
        'page-size': 'A4',
        'page-height': "13in",
        'page-width': "10in",
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': "UTF-8",
        'no-outline': None
    }

    template_path = 'salajuntas/formato_lista_asistencia.html'
    template = get_template(template_path)

    listado_participantes = ParticipantesReuniones.objects.filter(reunion_sala_de_juntas=reunion, is_active=True)

    datos_adicionales = [1,2,3,4,5]

    detalle_reunion = Reuniones.objects.get(pk=reunion)
    
    context = {
        "listado_participantes": listado_participantes,
        "reunion": detalle_reunion,
        "participantes_extra": datos_adicionales,
        "contador": 0
        }
    
    html = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf=wkhtml_to_pdf)

    pdf = pdfkit.from_string(html, False, configuration=config, options=options)

    # Generate download
    response = HttpResponse(pdf, content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="lista_asistencia.pdf"'

    if response.status_code != 200:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class SalaVistaGeneral(TemplateView):
    template_name = 'salajuntas/salageneral.html'

    def get_context_data(self, **kwargs):
        context = super(SalaVistaGeneral, self).get_context_data(**kwargs)
        context['catalogos_salas'] = Sala.objects.order_by('id') # No se filtra por salas activas porque se listarán todas las salas
        context['salas_catalogos'] = Sala.objects.order_by('ordenamiento')

        context['categorias'] = Categoria.objects.order_by('id')
        context['areas'] = Areas.objects.order_by('id')

        today = datetime.now()
        date_ini = str(today.year) + "-" + str(today.month) + "-" + "01"
        date_end = today.replace(day = calendar.monthrange(today.year, today.month)[1]).strftime("%Y-%m-%d")

        horarios = [
            {"value":"08:30", "hora": "08:30 a.m."},
            {"value":"09:00", "hora": "09:00 a.m."},
            {"value":"09:30", "hora": "09:30 a.m."},
            {"value":"10:00", "hora": "10:00 a.m."},
            {"value":"10:30", "hora": "10:30 a.m."},
            {"value":"11:00", "hora": "11:00 a.m."},
            {"value":"11:30", "hora": "11:30 a.m."},
            {"value":"12:00", "hora": "12:00 p.m."},
            {"value":"12:30", "hora": "12:30 p.m."},
            {"value":"13:00", "hora": "01:00 p.m."},
            {"value":"13:30", "hora": "01:30 p.m."},
            {"value":"14:00", "hora": "02:00 p.m."},
            {"value":"14:30", "hora": "02:30 p.m."},
            {"value":"15:00", "hora": "03:00 p.m."},
            {"value":"15:30", "hora": "03:30 p.m."},
            {"value":"16:00", "hora": "04:00 p.m."},
            {"value":"16:30", "hora": "04:30 p.m."},
            {"value":"17:00", "hora": "05:00 p.m."},
            {"value":"17:30", "hora": "05:30 p.m."},
            {"value":"18:00", "hora": "06:00 p.m."},
            {"value":"18:30", "hora": "06:30 p.m."},
            {"value":"19:00", "hora": "07:00 p.m."},
            {"value":"19:30", "hora": "07:30 p.m."},
            {"value":"20:00", "hora": "08:00 p.m."},
            {"value":"20:30", "hora": "08:30 p.m."},
            {"value":"21:00", "hora": "09:00 p.m."},
            {"value":"21:30", "hora": "09:30 p.m."},
            {"value":"22:00", "hora": "10:00 p.m."},
            {"value":"22:30", "hora": "10:30 p.m."},
            {"value":"23:00", "hora": "11:00 p.m."}
        ]

        context["accion_editar_sala"] = 0
        if User.objects.filter(username=self.request.user.username, groups__name__in=['SALA DE JUNTAS ADMINISTRADOR']).exists():
            context["accion_editar_sala"] = 1
        
        context["accion_buscar_sala"] = 0
        if User.objects.filter(username=self.request.user.username, groups__name__in=['SALA DE JUNTAS DIRECTIVOS', 'SALA DE JUNTAS ASISTENTES']).exists():
            context["accion_buscar_sala"] = 1

        context["horas_disponibles"] = horarios
        context['reuniones'] = Reuniones.objects.filter(is_active=True)
        context['usuarios'] = User.objects.filter(is_active=True)

        return context

def BuscarSalasDisponibles(request):
    FormData = request.POST

    fecha = FormData['fecha_reunion']
    hora_inicio = FormData['filter-hora_inicio']
    hora_fin = FormData['filter-hora_final']
    cantidad_personas = FormData['filter-total_participantes']

    # today = datetime.datetime.now()

    cursor = connection.cursor()
    sql = f'''
        SELECT DISTINCT reuniones.sala_id, ss.capacidad_sala 
        FROM saladejuntas_reuniones reuniones 
        LEFT JOIN saladejuntas_sala ss on ss.id = reuniones.sala_id
        WHERE reuniones.is_active = TRUE AND ss.is_active = TRUE AND reuniones.fecha_reunion = '{fecha}' AND reuniones.hora_ini_reunion >= '{hora_inicio}' AND reuniones.hora_ini_reunion <= '{hora_fin}' 
        GROUP BY reuniones.sala_id, ss.capacidad_sala, reuniones.id;
    '''
    cursor.execute(sql)

    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        for field in zip(fieldnames, row):
            rowset.append(field)
        result.append(dict(rowset))
    
    salas = list(Sala.objects.filter(capacidad_sala__gte=0, is_active=True).values("descripcion", "capacidad_sala", "id", "color", "color_name","detalle_descripcion").order_by('id'))

    return JsonResponse({'error': False, 'reuniones_activas': result, "salas_disponibles": salas, 'msj': "" })

def BuscarInformacionSala(request):
    FormData = request.POST

    id_sala = FormData['sala_id']

    salas = list(Sala.objects.filter(id=id_sala).values("descripcion", "capacidad_sala", "color", "color_name","detalle_descripcion").order_by('id'))

    return JsonResponse({'error': False, "data": salas, 'msj': "" })

def ActualizarInfoSala(request):
    FormData = request.POST

    if not FormData["sala_id"]:
        ramdon_color1 = random.randint(1, 50)
        ramdon_color2 = random.randint(1, 50)
        sala = Sala.objects.create(
            descripcion = FormData["sala_descripcion"], 
            detalle_descripcion = FormData["sala_detalle_descripcion"],
            capacidad_sala = FormData["sala_capacidad_sala"],
            color_name = "bg-color" + str(ramdon_color1) + str(ramdon_color2),
            color = FormData["sala_color"],
        ).save()
    else:
        sala_instance = Sala.objects.get(pk=FormData["sala_id"])
        sala_instance.descripcion = FormData["sala_descripcion"]
        sala_instance.detalle_descripcion = FormData["sala_detalle_descripcion"]
        sala_instance.capacidad_sala = FormData["sala_capacidad_sala"]
        sala_instance.color = FormData["sala_color"]
        sala_instance.save()

    return JsonResponse({'error': False, "data": FormData, 'msj': "" })

def ActivarDesactivarSalas(request):
    FormData = request.POST

    msj_exito = "Sala desactivada correctamente"
    estado_sala = False 
    if FormData["estado"] == "1":
        msj_exito = "Sala activada correctamente"
        estado_sala = True
    # now = datetime.datetime.now()
    sala_instance = Sala.objects.get(pk=FormData["sala_id"])
    sala_instance.is_active = estado_sala
    sala_instance.save() 

    

    return JsonResponse({'error': False, 'msj': msj_exito })

def BuscarSalas(request):
    FormData = request.POST

    mes_ini = FormData['filter-mes_ini']
    mes_fin = FormData['filter-mes_fin']
    anyo_ini = FormData['filter-anyo_ini']   
    anyo_fin = FormData['filter-anyo_fin']

    fecha_ini = str(anyo_ini)+ "-" + str(mes_ini) + "-01"

    if mes_ini == mes_fin:
        calendar_period = calendar.monthrange(int(anyo_ini), int(mes_ini))
        day = calendar_period[1]
        fecha_fin = str(anyo_ini) + "-" + str(mes_ini) + "-" + str(day)
    else:
        calendar_period = calendar.monthrange(int(anyo_fin), int(mes_fin))
        day = calendar_period[1]
        fecha_fin = str(anyo_fin) + "-" + str(mes_fin) + "-" + str(day)

    cursor = connection.cursor()
    sql = f'''
    SELECT reuniones.evento, reuniones.responsable_reunion, 
            reuniones.hora_ini_reunion, reuniones.hora_fin_reunion, 
            TO_CHAR(reuniones.fecha_reunion::date, 'dd/mm/yyyy') 
            as fecha_reunion,sala.color as sala_color , sc.descripcion as categoria, 
            reuniones.tiempo_coffe_break, reuniones.requiere_coffe_break, ua.nombre as area
            FROM saladejuntas_reuniones reuniones
            LEFT JOIN saladejuntas_categoria sc ON sc.id = reuniones.categoria_id
            LEFT JOIN users_areas ua ON ua.id = reuniones.area_id
            LEFT JOIN saladejuntas_sala sala on sala.id = reuniones.sala_id
            WHERE reuniones.is_active = TRUE AND sala.is_active = TRUE;
    '''
    cursor.execute(sql)

    fieldnames = [name[0] for name in cursor.description]
    result = []
    for row in cursor.fetchall():
        rowset = []
        for field in zip(fieldnames, row):
            rowset.append(field)
        result.append(dict(rowset))

    return JsonResponse({'error': False, 'data': result, 'msj': "Calendario actualizado correctamente" })

def OrdenarSala(request):  
    FormData = request.POST
        
    for key,value in FormData.items():      
        if 'order_' in key:
            id_sala = key[6:len(key)]
            sala_instance = Sala.objects.get(pk=id_sala)
            sala_instance.ordenamiento = value   
            sala_instance.is_active = False       
            sala_instance.save()

    for key,value in FormData.items():   
        
       if 'estat_' in key:
            estado = True
            if value == 'False':
                estado = False

            id_sala = key[6:len(key)]
            sala_instance = Sala.objects.get(pk=id_sala)   
            sala_instance.is_active = estado      
            sala_instance.save()

    return JsonResponse({'error': False,  'msj': "Calendario actualizado correctamente" })
