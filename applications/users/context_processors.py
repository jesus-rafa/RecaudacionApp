from datetime import date, datetime, timedelta
from applications.juridico.models import Demanda
from applications.users.models import Accesos
from applications.oficios.models import CC, CCO, Oficios, Recibidos
from applications.programacion.models import Programa
from applications.transferidos.models import Programa_Transferidos
from applications.users.models import User
from django.db.models import Q

def get_access(request):
    username = request.user.username
    perfil = []
    menu = []
    notificaciones = []
    mostrar = []
    total_notificaciones = []

    for group in request.user.groups.all():
        perfil.append(group.id)

    obj_access = Accesos.objects.filter(perfil__in=perfil)

    for page in obj_access:
        for url in page.urls.filter(is_active=True, is_visible=True).prefetch_related('get_urls').order_by('sort'):
            if url not in menu:
                menu.append(url)
            if url.tags != None:
                if url not in notificaciones:
                    notificaciones.append(url)

    def get_hijos(nivel, nombre, url, icono, padre_id, source):
        result = {'nivel': nivel,'nombre':nombre, 'url': url, 'icono': icono, 'padre': padre_id, 'hijos':[]}
        for url in source: 
            if url.padre.id == padre_id:
                hijos = get_hijos(url.nivel, url.nombre, url.url, url.icono, url.id, source)
                result['hijos'].append(hijos)
        return result
    
    menu_nuevo = get_hijos(0, 'root', '-', '-', 41, menu)

    for item in notificaciones:
        if item.tags == 'get_count_folios':
            num1 = 0
            if User.objects.filter(username=username, groups__name__contains='EJECUTIVO ANALISIS').exists():
                num_new = Programa.objects.filter(usuario=username, estatus='NUEVO').count()
                num_rej = Programa.objects.filter(usuario=username, estatus='1-RECHAZADA').count()
                num1 = num_new + num_rej
                comentarios = 'Por Publicar:' + str(num_new) + '<br>Rechazadas: ' + str(num_rej)

            elif User.objects.filter(username=username, groups__name__contains='COORDINACION PROGRAMACION').exists():
                num_new = Programa.objects.filter(estatus='PROPUESTA').count()
                num_rej = Programa.objects.filter(estatus='2-RECHAZADA').count()
                num1 = num_new + num_rej
                comentarios = 'Por Publicar:' + str(num_new) + '<br>Rechazadas: ' + str(num_rej)

            elif User.objects.filter(username=username, groups__name__contains='COORDINACION VIGILANCIA').exists():
                num_new = Programa.objects.filter(estatus__in=['FAFD', 'OFICIO']).count()
                num_rej = Programa.objects.filter(estatus='3-RECHAZADA').count()
                num1 = num_new + num_rej
                comentarios = 'Por Publicar:' + str(num_new) + '<br>Rechazadas: ' + str(num_rej)

            elif User.objects.filter(username=username, groups__name__contains='DIRECTOR').exists():
                num1 = Programa.objects.filter(estatus__in=['PRESUNTIVA']).count()
                comentarios = 'Fichas por Publicar'
            
            if num1 > 0:
                item.total = num1
                item.comentarios = comentarios
                total_notificaciones.append(num1)
                mostrar.append(item)

        elif item.tags == 'get_count_transfer': 
            num2 = Programa.objects.filter(
                estatus='PROPUESTA TRANSFERENCIA'
            ).count()

            if num2 > 0:
                item.total = num2
                item.comentarios = 'Contribuyentes para Transferir'
                total_notificaciones.append(num2)
                mostrar.append(item)

        elif item.tags == 'get_count_auditoria':
            num3 = Programa_Transferidos.objects.filter(
                is_active=True, estatus='TRANSFERIDO', area='AUDITORIA'
            ).count()

            if num3 > 0:
                item.total = num3
                item.comentarios = 'Contribuyentes por Revisar'
                total_notificaciones.append(num3)
                mostrar.append(item)

        elif item.tags == 'count_seguimiento':
            num4 = Programa.objects.filter(
                seguimiento=username, estatus='VALIDACION'
            ).count()

            num5 = Programa.objects.filter(
                seguimiento=username, estatus='RECHAZADO'
            ).count()

            if num4 != 0 and num5 != 0:
                item.total = num4 + num5
                item.comentarios = 'NUEVOS:' + str(num4) + '<br>RECHAZADOS: ' + str(num5)
                total_notificaciones.append(num4 + num5)
                mostrar.append(item)

        elif item.tags == 'count_notif_juridico':
            today = date.today()
            tomorrow = today + timedelta(days=3)
            num6 = Demanda.objects.filter(fecha_interno__gt = today, fecha_interno__lt = tomorrow).count()

            if num6 > 0:
                item.total = num6
                item.comentarios = 'Juicios por Vencer'
                total_notificaciones.append(num6)
                mostrar.append(item)

    oficios = Oficios.objects.filter(usuario=username, estatus='EN PROCESO').count()
    if oficios > 0:
        url = {}
        url['url'] = '/panel/0/0'
        url['nombre'] = 'Correspondencia'
        url['total'] = oficios
        url['comentarios'] = 'Oficios Enviados: EN PROCESO'
        mostrar.append(url)
        total_notificaciones.append(oficios)

    copia_oficios = CC.objects.filter(user__username=username, visto=False).count()
    if copia_oficios > 0:
        url = {}
        url['url'] = '/panel/0/0'
        url['nombre'] = 'Correspondencia'
        url['total'] = copia_oficios
        url['comentarios'] = 'Oficios Enviados: Para Conocimiento'
        mostrar.append(url)
        total_notificaciones.append(copia_oficios)

    recibidos = Recibidos.objects.filter(usuario=username, estatus='EN PROCESO').count()
    if recibidos > 0:
        url = {}
        url['url'] = '/panel/0/0'
        url['nombre'] = 'Correspondencia'
        url['total'] = recibidos
        url['comentarios'] = 'Oficios Recibidos: EN PROCESO'
        mostrar.append(url)
        total_notificaciones.append(recibidos)
        
    recibidos_para = Recibidos.objects.filter(~Q(pdf=''), para=username, estatus='EN PROCESO').count()
    if recibidos_para > 0:
        url = {}
        url['url'] = '/panel/0/0'
        url['nombre'] = 'Correspondencia'
        url['total'] = recibidos_para
        url['comentarios'] = 'Oficios Recibidos por Revisar'
        mostrar.append(url)
        total_notificaciones.append(recibidos_para)

    copia_recibidos = CCO.objects.filter(user__username=username, visto=False, tipo='C').count()
    if copia_recibidos > 0:
        url = {}
        url['url'] = '/panel/0/0'
        url['nombre'] = 'Correspondencia'
        url['total'] = copia_recibidos
        url['comentarios'] = 'Oficios Recibidos: Para Conocimiento'
        mostrar.append(url)
        total_notificaciones.append(copia_recibidos)

    turnados_recibidos = CCO.objects.filter(user__username=username, visto=False, tipo='T').count()
    if turnados_recibidos > 0:
        url = {}
        url['url'] = '/panel/0/0'
        url['nombre'] = 'Correspondencia'
        url['total'] = turnados_recibidos
        url['comentarios'] = 'Oficios Recibidos: Turnados'
        mostrar.append(url)
        total_notificaciones.append(turnados_recibidos)

    try:
        for p in request.user.plantilla.all():
            orientacion = p.orientacion
            color = p.menu
            barra = p.barra
    except:
        orientacion = 0
        color = 0
        barra = 1

    return {
        'menu': menu_nuevo,
        'notificaciones': mostrar,
        'total': sum(total_notificaciones),
        'orientacion': orientacion,
        'color': color,
        'barra': barra
    }
