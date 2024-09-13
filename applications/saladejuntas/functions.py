from django.conf import settings

from datetime import datetime, timedelta
import os
from os import path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import ssl, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage

import re
from .models import HistoricoReuniones


SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = './credentials.json'

def get_calendar_service():
    creds = None

    if os.path.exists('./token.pickle'):
        with open('./token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('./token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def add_historico_reuniones(request, reunion_instance, user_instance, estatus_instance, accion):
    # Agregar registro al historial de la agenda de reuniones
    HistoricoReuniones.objects.create(
        reunion_sala_de_juntas = reunion_instance, 
        descripcion = accion, 
        usuario = user_instance, 
        estatus = estatus_instance
    ).save()

def es_correo_valido(correo):
    expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, correo) is not None

def crear_evento(nombre_evento, desc_evento, fecha_hora_inicio, fecha_hora_fin, calendario_id, participantes):
    event_title = nombre_evento
    event_desc = desc_evento
    start_date = datetime.fromisoformat(str(fecha_hora_inicio)).isoformat()
    end_date = datetime.fromisoformat(str(fecha_hora_fin)).isoformat()

    calendar_service = get_calendar_service() 
    evento_result = calendar_service.events().insert(calendarId=str(calendario_id),
        body={
            "summary": event_title,
            "description": event_desc,
            "start": {
                "dateTime": start_date, 
                "timeZone": 'America/Mexico_City'
            },
            "end": {
                "dateTime": end_date, 
                "timeZone": 'America/Mexico_City'
            },
            "sendNotifications" : True,
            "attendees" : participantes
        },
        sendUpdates = 'all'
    ).execute()

    return evento_result['id']

def eliminar_evento(calendario_id, evento_id):
    calendar_service = get_calendar_service() 
    result_event = calendar_service.events().delete(calendarId=str(calendario_id), eventId=str(evento_id), sendUpdates = 'all').execute()
    return result_event

def enviar_correo(email_subject, receiver_email_address, content_email, title_content_email):
    sender_email = "heriberto.alvarado@guanajuato.gob.mx"
    receiver_email = receiver_email_address
    password = "Chem@653021"

    message = MIMEMultipart("alternative")
    message["Subject"] = email_subject
    message["From"] = "Reuniones SATEG <heriberto.alvarado@guanajuato.gob.mx>"
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    Reunión en Sala Ejecutiva 1 el día 02/02/2023 de 08:30 a 09:00 hrs.
    Detalles del Coffe Break:
    Se necesita de café y galletitas

    --
    Administración del correo electrónico de Gobierno del Estado de Guanajuato.
    SERVICIO DE ADMINISTRACIÓN TRIBUTARIA DEL ESTADO DE GUANAJUATO
    
    Nota: Favor de no responder a esta dirección de correo electrónico."""

    html = content_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
        server.quit()
