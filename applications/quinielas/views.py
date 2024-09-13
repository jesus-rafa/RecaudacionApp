import pytz
from datetime import datetime, timezone
from django.shortcuts import render
from .models import Partidos, Pronostico, Equipos, User
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, View)
from django.http.response import JsonResponse
from applications.users.functions import get_id_user
from django.db import connection
# from applications.users.mixins import GlobalMixin

# Create your views here.

class Pronostico_View(TemplateView):
    template_name = 'quinielas/pronostico.html'

    def get_context_data(self, **kwargs):
        context = super(Pronostico_View, self).get_context_data(**kwargs)

        cursor = connection.cursor()    
        sql = f'''select * from pronostico_user({self.request.user.id});'''
        print(sql)
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        context['partidos'] = result

        cursor = connection.cursor()    
        sql = f'''SELECT distinct fecha_hora::date, CASE WHEN current_timestamp < fecha_hora::date THEN 1 ELSE 0 END AS d_no_disponible 
                FROM quinielas_partidos order by fecha_hora;'''
        print(sql)
        cursor.execute(sql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        context['fechas'] = result

        context['pronostico'] = Pronostico.objects.filter(usuario_id=get_id_user(self)).order_by('partido__fecha_hora')

        dt = datetime.now() 
        dt = dt.replace(tzinfo=timezone.utc)
        context['hoy'] = dt

        return context

def Crea_Pronostico(request):

    FormData = request.POST
    
    partido_intance = Partidos.objects.get(pk=FormData['partido'])
    user_instance = User.objects.get(pk=request.user.id)

    dt = datetime.now()
    dt = dt.replace(tzinfo=timezone.utc)

    if (partido_intance.fecha_hora < dt):
        return JsonResponse({'result': 
                                {
                                    'error' : '¡Fuera de tiempo!' 
                                }
                            })
    
    msj = '¡Registro guardado!'
    pronostico = Pronostico.objects.filter(usuario=request.user.id,partido=FormData['partido'])

    if pronostico:
        msj = '¡Registro actualizado!'
        for line in pronostico:
            pronostico_instance = Pronostico.objects.get(pk=line.id)
            pronostico_instance.pronostico = FormData['pronostico']
            pronostico_instance.pronostico_local = FormData['local']
            pronostico_instance.pronostico_visitante = FormData['visitante']
            pronostico_instance.save()
    else:
        Pronostico.objects.create(
            partido = partido_intance, 
            usuario = user_instance, 
            pronostico = FormData['pronostico'], 
            pronostico_local = FormData['local'],
            pronostico_visitante = FormData['visitante'],
        ).save()

    return JsonResponse({'result': 
                            {
                                'exito' : msj,
                            }
                        })
    
def Edita_Pronostico(request):

    FormData = request.POST

    pronostico_instance = Pronostico.objects.get(pk=FormData['id_pronostico'])
    partido_intance = Partidos.objects.get(pk=pronostico_instance.partido.id)

    dt = datetime.now()
    dt = dt.replace(tzinfo=timezone.utc)

    if (partido_intance.fecha_hora < dt):
        return JsonResponse({'result': '¡Fuera de tiempo!' })

    pronostico_instance.pronostico = FormData['pronostico']
    pronostico_instance.pronostico_local = FormData['local']
    pronostico_instance.pronostico_visitante = FormData['visitante']
    pronostico_instance.save()

    return JsonResponse({'result': '¡Registro actualizado!' })

class ReportePronosticos( ListView):
    template_name = 'quinielas/reportes/resultados_pronosticos.html'
    model = Pronostico
    context_object_name = 'pronosticos'

    def get_queryset(self):
        kword = self.request.GET.get("kword", '')
        tz_mx = pytz.timezone('America/Mexico_City')
        hoy = datetime.now(tz_mx)

        if kword:
            QuerySet = Pronostico.objects.filter(partido__fecha_hora__lt=hoy, partido__id=kword)
        else:
            QuerySet = Pronostico.objects.filter(partido__fecha_hora__lt=hoy, partido__id=1)

        return QuerySet
        
    def get_context_data(self, **kwargs):
        context = super(ReportePronosticos, self).get_context_data(**kwargs)
        kword = self.request.GET.get("kword", '')
        
        tz_mx = pytz.timezone('America/Mexico_City')
        hoy = datetime.now(tz_mx)

        context["hoy"] = hoy

        option_selectize = "1"
        if kword:
            option_selectize = kword

        context['option_selectize'] = option_selectize
        if option_selectize:
            context["resultado_partido"] = Partidos.objects.filter(id=option_selectize)
        context["partidos"] = Partidos.objects.filter(fecha_hora__lte=hoy).order_by('fecha_hora')

        return context

class Tabulador_Quiniela_View(ListView):
    template_name = 'quinielas/reportes/ranking.html'
    model = Pronostico
    context_object_name = 'ranking'

    def get_queryset(self):
        tz_mx = pytz.timezone('America/Mexico_City')
        hoy = datetime.now(tz_mx)

        query = f"""
            SELECT qp.usuario_id, 
                (
                    SELECT sum(qp2.puntos) 
                    FROM quinielas_pronostico qp2 
                    WHERE qp2.usuario_id = qp.usuario_id 
                ) AS total_puntos,
                (
                    SELECT UPPER(CONCAT(uu.nombres, ' ', uu.apellidos)) 
                    FROM users_user uu 
                    WHERE uu.id = qp.usuario_id
                ) AS usuario,
                (
                    SELECT COUNT(*) 
                    FROM quinielas_partidos
                ) AS total_partidos,
                (
                    SELECT COUNT(*) 
                    FROM quinielas_partidos qp3 
                    WHERE qp3.fecha_hora <= '""" + str(hoy) + """'
                ) AS partidos_jugados,
                (
                    SELECT COUNT(*)
                    FROM quinielas_pronostico q_pronostico 
                    INNER JOIN quinielas_partidos q_partidos ON q_partidos.id = q_pronostico.partido_id 
                    WHERE q_pronostico.usuario_id = qp.usuario_id and q_pronostico.pronostico = q_partidos.ganador
                ) AS total_partidos_acertados,
                (
                    SELECT COUNT(*) 
                    FROM quinielas_pronostico q_pronostico1 
                    INNER JOIN quinielas_partidos q_partidos1 on q_partidos1.id = q_pronostico1.partido_id 
                    WHERE q_pronostico1.usuario_id = qp.usuario_id and q_pronostico1.pronostico_local = q_partidos1.resultado_local and q_pronostico1.pronostico_visitante = q_partidos1.resultado_visitante and q_partidos1.ganador > 0
                ) AS total_marcador_partidos_acertados
            FROM quinielas_pronostico qp 
            GROUP BY qp.usuario_id
            ORDER BY total_puntos DESC
        """
        cursor = connection.cursor()
        cursor.execute(query)

        fieldnames = [name[0] for name in cursor.description]
        # Agregamos el nombre de la columna adicional que se necesita
        fieldnames.append("posicion")

        queryset = []
        ranking = 1
        total = 0
        for row in cursor.fetchall():

            # Convertimos la trupla a array para poder iterar
            row_tmp = list(row)
            # Partimos de la posición 0 validando el total de puntos acumulados por usuario
            if total == 0:
                # Agregamos el ranking actual
                row_tmp.append(ranking)
                # Actualizamos la variable de total acumulado
                total = row_tmp[1]
            else:
                # Validamos si total de cada registro es menor al de la posición actual
                if row_tmp[1] < total:
                    # Aumentamos una posición al raking
                    ranking += 1
                    total = row_tmp[1]

                # Siempre agregamos el ranking actual a cada registro
                row_tmp.append(ranking)

            rowset = []
            for field in zip(fieldnames, row_tmp):
                rowset.append(field) 

            queryset.append(dict(rowset))

        return queryset
