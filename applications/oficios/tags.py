from datetime import date, datetime, timedelta

from applications.juridico.models import Archivos_Juridico
from applications.oficios.models import CC, CCO, Oficios, Recibidos
from applications.programacion.models import Programa
from applications.transferidos.models import Programa_Transferidos
from applications.users.models import User
from django import template
from django.utils.timesince import timesince
from django.db.models import Q
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def dias_html(dias):
    span = ''

    if dias != 'None':

        if dias > 3:
            color = 'bg-success'
        elif dias <= 3 and dias > 0:
            color = 'bg-danger'
        elif dias == 0 or dias == '0':
            color = 'bg-danger'
        else:
            color = 'bg-dark'

        span = ('<span style="font-size: 12px;" class="position-absolute top-0 start-100 translate-middle badge rounded-circle noti-icon-badge ' + color + '" title="dias de vencimiento" tabindex="0" data-plugin="tippy" data-tippy-placement="right">' + str(dias) + '</span>')

    return mark_safe(span)


@register.filter
def get_age(value):
    difference = None
    try:
        difference = value - timedelta(hours=6)
    except:
        return value

    return difference


@register.filter
def split(value):
    data = value.split('_')
    return data[0], data[1]


@register.simple_tag
def get_count_folios(username):

    try:

        if User.objects.filter(username=username, groups__name__contains='EJECUTIVO ANALISIS').exists():
            count = Programa.objects.filter(usuario=username, estatus__in=['NUEVO', '1-RECHAZADA']).count()

        elif User.objects.filter(username=username, groups__name__contains='COORDINACION PROGRAMACION').exists():
            count = Programa.objects.filter(estatus__in=['PROPUESTA', '2-RECHAZADA']).count()

        elif User.objects.filter(username=username, groups__name__contains='COORDINACION VIGILANCIA').exists():
            count = Programa.objects.filter(estatus__in=['FAFD', 'OFICIO', '3-RECHAZADA']).count()

        elif User.objects.filter(username=username, groups__name__contains='DIRECTOR').exists():
            count = Programa.objects.filter(estatus__in=['PRESUNTIVA']).count()
        else:
            count = 0

    except:
        count = 0

    # if count == 0:
    #    count = ''

    return count


@register.simple_tag
def get_estatus(oficio, username):

    try:

        if CCO.objects.filter(oficio=oficio, enviado_por=username, tipo='T').exists():
            estatus = 1
        else:
            estatus = 0

    except:
        estatus = 0

    return estatus


@register.simple_tag
def get_count_correspondencia(username):

    try:

        oficios = Oficios.objects.filter(
            usuario=username, estatus='EN PROCESO').count()

        copia_oficios = CC.objects.filter(
            user__username=username, visto=False).count()

        recibidos = Recibidos.objects.filter(
            usuario=username, estatus='EN PROCESO').count()

        recibidos_para = Recibidos.objects.filter(
            ~Q(pdf=''), para=username, estatus='EN PROCESO').count()

        copia_recibidos = CCO.objects.filter(
            user__username=username, visto=False).count()

        count = oficios + copia_oficios + recibidos + recibidos_para + copia_recibidos

    except:
        count = 0

    return count


@register.simple_tag
def get_user_info(username):

    try:
        user = User.objects.filter(username=username)
        name = user[0].nombres + ' ' + user[0].apellidos
    except:
        name = ''

    return name


@register.simple_tag
def get_user_id(username):

    try:
        user = User.objects.filter(username=username)
        id = user[0].id
    except:
        id = 0

    return id


@register.simple_tag
def get_user_avatar(username):

    try:
        user = User.objects.filter(username=username)
        avatar = user[0].avatar.url
    except:
        avatar = ''

    return avatar


@register.simple_tag
def get_initials(username):

    try:
        user = User.objects.filter(username=username)
        name = user[0].nombres[:1] + user[0].apellidos[:1]
    except:
        name = ''

    return name


@register.simple_tag
def notificacion(num1, num2, num3, num4):

    try:
        flag = False

        if num1 is None or num1 == '':
            num1 = 0
        if num2 is None or num2 == '':
            num2 = 0
        if num3 is None or num3 == '':
            num3 = 0
        if num4 is None or num4 == '':
            num4 = 0

        aux = int(num1) + int(num2) + int(num3) + int(num4)

        if aux > 0:
            flag = True

    except:
        flag = False

    return flag


@register.simple_tag
def sum_notificacion(num1, num2, num3, num4, num5, num6, num7):

    try:

        if num1 is None or num1 == '':
            num1 = 0
        if num2 is None or num2 == '':
            num2 = 0
        if num3 is None or num3 == '':
            num3 = 0
        if num4 is None or num4 == '':
            num4 = 0
        if num5 is None or num5 == '':
            num5 = 0
        if num6 is None or num6 == '':
            num6 = 0
        if num7 is None or num7 == '':
            num7 = 0

        aux = int(num1) + int(num2) + int(num3) + \
            int(num4) + int(num5) + int(num6) + int(num7)

    except:
        aux = 0

    return aux


@register.simple_tag
def getProgramaID(folio):

    try:
        obj = Programa.objects.filter(folio=folio)
        id = obj[0].id
    except:
        id = 0

    return id


@register.simple_tag
def replace_url(folio):

    try:
        new_folio = folio.replace('/', '-')
    except:
        new_folio = '1'

    return new_folio


@register.filter
def replace_data(value):
    return value.replace('a', '').replace('b', '').replace('c', '').replace('d', '').replace('e', '').replace('f', '').replace('g', '').replace('h', '').replace('i', '').replace('j', '').replace('k', '').replace('l', '')


@register.simple_tag
def get_oficio(folio):

    try:
        obj = Oficios.objects.filter(folio=folio)
        oficio = obj[0].pdf.url
    except:
        oficio = ''

    return oficio


@register.simple_tag
def get_color(index):

    colores = ['#0D47A1', '#1565C0', '#1976D2', '#1E88E5', '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB', '#E3F2FD', '#E3F2FD', '#0D47A1', '#1565C0', '#1976D2', '#1E88E5', '#42A5F5',
               '#64B5F6', '#90CAF9', '#BBDEFB', '#E3F2FD', '#E3F2FD', '#0D47A1', '#1565C0', '#1976D2', '#1E88E5', '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB', '#E3F2FD', '#E3F2FD']

    return colores[index]


@register.simple_tag
def get_count_transfer():

    try:
        count = Programa.objects.filter(
            estatus='PROPUESTA TRANSFERENCIA'
        ).count()

    except:
        count = 0

    return count


@register.simple_tag
def count_seguimiento(username, estatus):

    try:
        count = Programa.objects.filter(
            seguimiento=username,
            estatus=estatus
        ).count()

    except:
        count = 0

    return count


@register.simple_tag
def get_count_auditoria():

    try:

        count = Programa_Transferidos.objects.filter(
            is_active=True,
            estatus='TRANSFERIDO',
            area='AUDITORIA'
        ).count()

    except:
        count = 0

    # if count == 0:
    #    count = ''

    return count


@register.simple_tag
def dias_seguimiento(fecha_creacion):
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
def dias_vigilancia(fecha_concluido, fecha_creacion):

    try:
        dias = (fecha_concluido - fecha_creacion).days

    except:
        dias = 0

    return dias


@register.simple_tag
def get_count_ejecucion():

    try:

        count = Programa_Transferidos.objects.filter(
            is_active=True,
            estatus='TRANSFERIDO',
            area='EJECUCION'
        ).distinct('nuevo_folio').count()

    except:
        count = 0

    # if count == 0:
    #    count = ''

    return count


@register.simple_tag
def get_month(id):
    month = ''

    if id == 1:
        month = 'ENE'
    elif id == 2:
        month = 'FEB'
    elif id == 3:
        month = 'MAR'
    elif id == 4:
        month = 'ABR'
    elif id == 5:
        month = 'MAY'
    elif id == 6:
        month = 'JUN'
    elif id == 7:
        month = 'JUL'
    elif id == 8:
        month = 'AGO'
    elif id == 9:
        month = 'SEP'
    elif id == 10:
        month = 'OCT'
    elif id == 11:
        month = 'NOV'
    elif id == 12:
        month = 'DIC'

    return month


@register.simple_tag
def get_month_order(id):
    month = ''

    if id == 1:
        month = 'A'
    elif id == 2:
        month = 'B'
    elif id == 3:
        month = 'C'
    elif id == 4:
        month = 'D'
    elif id == 5:
        month = 'E'
    elif id == 6:
        month = 'F'
    elif id == 7:
        month = 'G'
    elif id == 8:
        month = 'H'
    elif id == 9:
        month = 'I'
    elif id == 10:
        month = 'J'
    elif id == 11:
        month = 'K'
    elif id == 12:
        month = 'L'

    return month


@register.simple_tag
def get_month_2(folio):

    index = folio.find('-')
    id = int(folio[:index])
    month = ''

    if id == 1:
        month = 'ENE'
    elif id == 2:
        month = 'FEB'
    elif id == 3:
        month = 'MAR'
    elif id == 4:
        month = 'ABR'
    elif id == 5:
        month = 'MAY'
    elif id == 6:
        month = 'JUN'
    elif id == 7:
        month = 'JUL'
    elif id == 8:
        month = 'AGO'
    elif id == 9:
        month = 'SEP'
    elif id == 10:
        month = 'OCT'
    elif id == 11:
        month = 'NOV'
    elif id == 12:
        month = 'DIC'

    no_control = month + folio[index:]
    
    return no_control
