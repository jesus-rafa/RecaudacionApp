from datetime import date, datetime, timedelta

from applications.juridico.models import Archivos_Juridico, Demanda
from applications.oficios.models import CC, CCO, Oficios, Recibidos
from applications.programacion.models import Programa
from applications.transferidos.models import Programa_Transferidos
from applications.users.models import User
from django import template
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.db.models import (Count, DurationField, ExpressionWrapper, F,
                              IntegerField, Q, Subquery, Sum, Value)

register = template.Library()

@register.simple_tag
def dias_restantes(fecha_creacion):
    try:
        dias = (fecha_creacion - date.today()).days       

    except:
        dias = 0

    return dias

@register.simple_tag
def dias_trasncurrido(fecha_creacion):
    fecha_creacion = fecha_creacion.date()
    try:
        dias = (date.today() - fecha_creacion).days
    except:
        dias = 0

    return dias

@register.simple_tag
def count_files(id_proceso):

    try:
        total_archivos = Archivos_Juridico.objects.filter(
            proceso=id_proceso
        ).count()

    except:
        total_archivos = 0

    return total_archivos
    
@register.simple_tag
def count_notif_juridico():
    try:
        today = date.today()
        tomorrow = today + datetime.timedelta(days=3)
        count = Demanda.objects.filter(fecha_interno__gt = today, fecha_interno__lt = tomorrow).count()
    except:
        count = 0

    return count

@register.simple_tag
def setBooleano(value):
    try:
        if value:
            return 'Si'
        else:
            return 'No'
    except:
        return 'Nada'