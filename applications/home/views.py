from datetime import date
from django.shortcuts import render
from django.views.generic import (
    TemplateView
)
from django.views.generic.list import ListView
from django.template import RequestContext
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db import connection
from applications.users.mixins import GlobalMixin
from django.views.generic import TemplateView


class InicioAuditoriaView(GlobalMixin, ListView):
    """ vista que carga la pagina de inicio """
    template_name = 'home/inicio_auditoria.html'
    login_url = reverse_lazy('users_app:login')
    context_object_name = 'recaudado'
    
    def get_queryset(self):
        QuerySet = None
        return QuerySet
        
        
class InicioEjecucionView(GlobalMixin, ListView):
    """ vista que carga la pagina de inicio """
    template_name = 'home/inicio_ejecucion.html'
    login_url = reverse_lazy('users_app:login')
    context_object_name = 'recaudado'
    
    def get_queryset(self):
        QuerySet = None
        return QuerySet
        
class InicioJuridicoView(GlobalMixin, TemplateView):
    """ vista que carga la pagina de inicio """
    template_name = 'home/inicio_juridico.html'
    login_url = reverse_lazy('users_app:login')

    def get_context_data(self, **kwargs):
        context = super(InicioJuridicoView, self).get_context_data(**kwargs)

        fecha_actual = date.today()

        if self.request.GET.get("inicio", '') == '' and self.request.GET.get("fin", '') == '':
            fecha_inicio = '01-01-' + str(fecha_actual.year)
            fecha_fin = '31-12-' + str(fecha_actual.year)
        else:
            fecha_inicio = str(self.request.GET.get("inicio", ''))
            fecha_fin = str(self.request.GET.get("fin", ''))


        # fecha_inicio = '01-01-2022'
        # fecha_fin = '31-12-2022'
        
        #NUMERO DE JUICIOS Y AVANCE POR TIPO 
        cursor = connection.cursor()
        mySql = f'''select juicios_,
                            estatal_,
                            federal_,
                            avance_estatal_,
                            avance_federal_
                    from avance_Juridico('{fecha_inicio}','{fecha_fin}')'''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        cursor.close()
        context['avance_juicios'] = result

        #NUMERO DE SENTENCIAS CON RESOLUCIONES 1RA INSTANCIA
        cursor = connection.cursor()
        mySql = f'''select *
                    from primera_instancia('{fecha_inicio}','{fecha_fin}')'''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        cursor.close()
        context['avance_sentencias_primera'] = result

        #NUMERO DE SENTENCIAS CON RESOLUCIONES 2DA INSTANCIA
        cursor = connection.cursor()
        mySql = f'''select *
                    from segunda_instancia('{fecha_inicio}','{fecha_fin}')'''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        cursor.close()
        context['avance_sentencias_segunda'] = result

        #NUMERO RR
        cursor = connection.cursor()
        mySql = f'''select *
                    from firmeza_indicadores('{fecha_inicio}','{fecha_fin}')'''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        cursor.close()
        context['context_firmeza'] = result

        #CONTESTACION NOTIFICACION
        cursor = connection.cursor()
        mySql = f'''select *
                    from notificacion_contestacion('{fecha_inicio}','{fecha_fin}')'''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        cursor.close()
        context['notificacion_contestacion'] = result

        # #SENTENCIAS 1RA INSTANCIA CUANTIA
        # cursor = connection.cursor()
        # mySql = f'''select *
        #             from notificacion_contestacion('{fecha_inicio}','{fecha_fin}')'''
        # cursor.execute(mySql)
        # fieldnames = [name[0] for name in cursor.description]
        # result = []
        # for row in cursor.fetchall():
        #     rowset = []
        #     for field in zip(fieldnames, row):
        #         rowset.append(field)
        #     result.append(dict(rowset))
        # cursor.close()
        # context['notificacion_contestacion'] = result

        #LISTADO FIRMEZA
        cursor = connection.cursor()
        mySql = f'''select *
                    from firmeza_listado('{fecha_inicio}','{fecha_fin}')'''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        cursor.close()
        context['firmeza_listado'] = result

        cursor11 = connection.cursor()
        mySql11 = f'''SELECT 
                        ejercicio,
                        periodo_,
                        estatal_,
                        federal_,
                        total_
                    FROM public.avance_mensual_Juicios('{fecha_inicio}','{fecha_fin}')
                    ORDER BY periodo_'''
        cursor11.execute(mySql11)
        fieldnames11 = [name[0] for name in cursor11.description]
        result11 = []
        for row in cursor11.fetchall():
            rowset = []
            for field in zip(fieldnames11, row):
                rowset.append(field)
            result11.append(dict(rowset))
        context['avance_mensual_Juicios'] = result11

        cursor8 = connection.cursor()
        mySql8 = f'''select ejercicio_, 
                           periodo_,
                           estatales_,
                           federales_,
                           total_
                    from avance_mensual_tramites('{fecha_inicio}','{fecha_fin}')'''
        cursor8.execute(mySql8)
        fieldnames8 = [name[0] for name in cursor8.description]
        result8 = []
        for row in cursor8.fetchall():
            rowset = []
            for field in zip(fieldnames8, row):
                rowset.append(field)
            result8.append(dict(rowset))
        context['avance_mensual_tramites'] = result8

        cursor10 = connection.cursor()
        mySql10 = f'''select total_, 
                        pago_total_, 
                        transferidas_, 
                        aclaracion_	
                    from public.fichas_concluidas('{fecha_inicio}','{fecha_fin}')'''
        cursor10.execute(mySql10)
        fieldnames10 = [name[0] for name in cursor10.description]
        result10 = []
        for row in cursor10.fetchall():
            rowset = []
            for field in zip(fieldnames10, row):
                rowset.append(field)
            result10.append(dict(rowset))
        context['fichas_concluidas'] = result10

        return context


    

class Home(LoginRequiredMixin, ListView):
    """ vista que carga la pagina de inicio """
    template_name = 'home/home.html'
    login_url = reverse_lazy('users_app:login')
    context_object_name = 'recaudado'
    
    def get_queryset(self):
        QuerySet = None
        return QuerySet

        
class InicioNewView(ListView):
    """ vista que carga la pagina de inicio """
    template_name = 'home/inicio_new.html'
    login_url = reverse_lazy('users_app:login')
    context_object_name = 'recaudado'
    
    def get_queryset(self):
        QuerySet = None
        return QuerySet
    

class InicioView(GlobalMixin, ListView):
    """ vista que carga la pagina de inicio """
    template_name = 'home/inicio.html'
    login_url = reverse_lazy('users_app:login')
    context_object_name = 'recaudado'
    
    def get_queryset(self):
        fecha_actual = date.today()

        if self.request.GET.get("year", '') == '':
            fecha_inicio = '01-01-' + str(fecha_actual.year)
            fecha_fin = '31-12-' + str(fecha_actual.year)
        else:
            fecha_inicio = '01-01-' + str(self.request.GET.get("year", ''))
            fecha_fin = '31-12-' + str(self.request.GET.get("year", ''))

        cursor = connection.cursor()
        mySql = f'''SELECT 
                    padrones_, 
                    programacion_, 
                    vigilancia_, 
                    promocion_,
                    total_, 
                    avance_ 
                FROM public.saldo_recaudacion('{fecha_inicio}','{fecha_fin}')'''

        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))

        queryset = result

        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(InicioView, self).get_context_data(**kwargs)

        fecha_actual = date.today()

        if self.request.GET.get("year", '') == '':
            fecha_inicio = '01-01-' + str(fecha_actual.year)
            fecha_fin = '31-12-' + str(fecha_actual.year)
        else:
            fecha_inicio = '01-01-' + str(self.request.GET.get("year", ''))
            fecha_fin = '31-12-' + str(self.request.GET.get("year", ''))

        cursor = connection.cursor()
        mySql = f''' SELECT
                        concluidos_,
                        presuntiva_concluidas_,
                        seguimiento_,
                        presuntiva_seguimiento_,
                        por_asignar_,
                        presuntiva_por_asignar_, 
                        transferencias_,
                        dias_,
                        efectividad_total_,
                        efectividad_
                    from public.avance_fafd('{fecha_inicio}','{fecha_fin}')'''
        cursor.execute(mySql)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        context['fafd'] = result
        
        cursor2 = connection.cursor()
        mySql2 = f'''select ejercicio,
                           periodo_,
                           vigilancia_,
                           padrones_,
                           programacion_,
                           promocion,
                           total_
                    from avance_mensual_recaudacion('{fecha_inicio}','{fecha_fin}')
                        order by periodo_'''
        cursor2.execute(mySql2)
        fieldnames2 = [name[0] for name in cursor2.description]
        result2 = []
        for row in cursor2.fetchall():
            rowset = []
            for field in zip(fieldnames2, row):
                rowset.append(field)
            result2.append(dict(rowset))
        context['avance_mensual_recaudacion'] = result2
        
        cursor3 = connection.cursor()
        mySql3 = f'''select cartas_,
                            correos_,
                            efectividad_cartas_,
                            efectividad_correos_,
                            total_
                    from avance_invitaciones('{fecha_inicio}','{fecha_fin}')'''
        cursor3.execute(mySql3)
        fieldnames3 = [name[0] for name in cursor3.description]
        result3 = []
        for row in cursor3.fetchall():
            rowset = []
            for field in zip(fieldnames3, row):
                rowset.append(field)
            result3.append(dict(rowset))
        context['avance_invitaciones'] = result3
        
        cursor4 = connection.cursor()
        mySql4 = f'''select periodo_,
                           autorizadas_,
                           notificadas_,
                           entrevista_,
                           concluidas
                    from avance_mensual_fafd('{fecha_inicio}','{fecha_fin}')
                        order by periodo_'''
        cursor4.execute(mySql4)
        fieldnames4 = [name[0] for name in cursor4.description]
        result4 = []
        for row in cursor4.fetchall():
            rowset = []
            for field in zip(fieldnames4, row):
                rowset.append(field)
            result4.append(dict(rowset))
        context['avance_mensual_fafd'] = result4
        
        
        cursor5 = connection.cursor()
        mySql5 = f'''select programa_, 
                           presuntiva_, 
                           padrones_, 
                           programacion_, 
                           vigilancia_,
                           promocion, 
                           total_
                    from avance_por_programa('{fecha_inicio}','{fecha_fin}')
                        order by programa_'''
        cursor5.execute(mySql5)
        fieldnames5 = [name[0] for name in cursor5.description]
        result5 = []
        for row in cursor5.fetchall():
            rowset = []
            for field in zip(fieldnames5, row):
                rowset.append(field)
            result5.append(dict(rowset))
        context['avance_x_programa'] = result5
        
        
        cursor6 = connection.cursor()
        mySql6 = F'''select
                        fafd_,
                        presuntiva_,
                        porcentaje_,
                        porcentaje2_,
                        porcentaje3_,
                        porcentaje_ + porcentaje3_ as total_,
                        propuesta_,
                        aprobadas_,
                        canceladas_, 
                        informativas,
                        aprobadas_ - informativas - fafd_ as transito_
                    from avance_fichas('{fecha_inicio}','{fecha_fin}')'''
        cursor6.execute(mySql6)
        fieldnames6 = [name[0] for name in cursor6.description]
        result6 = []
        for row in cursor6.fetchall():
            rowset = []
            for field in zip(fieldnames6, row):
                rowset.append(field)
            result6.append(dict(rowset))
        context['avance_fichas'] = result6
        
        
        cursor7 = connection.cursor()
        mySql7 = f'''select ejercicio_, 
                           periodo_, 
                           total_
                    from avance_mensual_contribuyentes('{fecha_inicio}','{fecha_fin}')'''
        cursor7.execute(mySql7)
        fieldnames7 = [name[0] for name in cursor7.description]
        result7 = []
        for row in cursor7.fetchall():
            rowset = []
            for field in zip(fieldnames7, row):
                rowset.append(field)
            result7.append(dict(rowset))
        context['avance_mensual_contribuyentes'] = result7
        
        
        cursor8 = connection.cursor()
        mySql8 = f'''select ejercicio_, 
                           periodo_,
                           estatales_,
                           federales_,
                           total_
                    from avance_mensual_tramites('{fecha_inicio}','{fecha_fin}')'''
        cursor8.execute(mySql8)
        fieldnames8 = [name[0] for name in cursor8.description]
        result8 = []
        for row in cursor8.fetchall():
            rowset = []
            for field in zip(fieldnames8, row):
                rowset.append(field)
            result8.append(dict(rowset))
        context['avance_mensual_tramites'] = result8
        
        
        cursor9 = connection.cursor()
        mySql9 = f'''select actividades_, 
                           total_,
                           porcentaje_
                    from public.actividades('{fecha_inicio}','{fecha_fin}')'''
        cursor9.execute(mySql9)
        fieldnames9 = [name[0] for name in cursor9.description]
        result9 = []
        for row in cursor9.fetchall():
            rowset = []
            for field in zip(fieldnames9, row):
                rowset.append(field)
            result9.append(dict(rowset))
        context['actividades'] = result9


        cursor10 = connection.cursor()
        mySql10 = f'''select total_, 
                        pago_total_, 
                        transferidas_, 
                        aclaracion_	
                    from public.fichas_concluidas('{fecha_inicio}','{fecha_fin}')'''
        cursor10.execute(mySql10)
        fieldnames10 = [name[0] for name in cursor10.description]
        result10 = []
        for row in cursor10.fetchall():
            rowset = []
            for field in zip(fieldnames10, row):
                rowset.append(field)
            result10.append(dict(rowset))
        context['fichas_concluidas'] = result10
        
        cursor11 = connection.cursor()
        mySql11 = f'''SELECT 
                        ejercicio,
                        periodo_,
                        vigilancia_,
                        padrones_,
                        programacion_,
                        promocion,
                        total_
                    FROM public.avance_mensual_recaudacion('{fecha_inicio}','{fecha_fin}')
                    UNION
                    SELECT 
                        0 ejercicio,
                        13 periodo_, 
                        SUM(A.vigilancia_) vigilancia_, 
                        SUM(A.padrones_) padrones_, 
                        SUM(A.programacion_) programacion_,
                        SUM(A.promocion) promocion, 
                        SUM (A.total_) total_
                    FROM public.avance_mensual_recaudacion('{fecha_inicio}','{fecha_fin}') AS A
                    ORDER BY periodo_'''
        cursor11.execute(mySql11)
        fieldnames11 = [name[0] for name in cursor11.description]
        result11 = []
        for row in cursor11.fetchall():
            rowset = []
            for field in zip(fieldnames11, row):
                rowset.append(field)
            result11.append(dict(rowset))
        context['resumen_recaudacion'] = result11

        return context


class Reporte_Moac(GlobalMixin, TemplateView):
    template_name = 'home/reporte_moac.html'
    login_url = reverse_lazy('users_app:login')   


class Reporte_IngresosView(GlobalMixin, TemplateView):
    template_name = 'home/reporte_ingresos.html'
    login_url = reverse_lazy('users_app:login')


class Reporte_VehicularView(GlobalMixin, TemplateView):
    template_name = 'home/reporte_vehicular.html'
    login_url = reverse_lazy('users_app:login')


class Padron_VehicularView(GlobalMixin, TemplateView):
    template_name = 'home/padron_vehicular.html'
    login_url = reverse_lazy('users_app:login')
    
    
class RECView(GlobalMixin, TemplateView):
    template_name = 'home/rec.html'
    login_url = reverse_lazy('users_app:login')
    
    
class OrganigramaView(GlobalMixin, TemplateView):
    template_name = 'home/organigrama.html'
    login_url = reverse_lazy('users_app:login')
    
    
class Reporte_Vigilancia(GlobalMixin, TemplateView):
    template_name = 'home/reporte_vigilancia.html'
    login_url = reverse_lazy('users_app:login')
    
class Reporte_Padrones(GlobalMixin, TemplateView):
    template_name = 'home/reporte_padrones.html'
    login_url = reverse_lazy('users_app:login')

class Nivel_Cumplimiento(GlobalMixin, TemplateView):
    template_name = 'home/nivel_cumplimiento.html'
    login_url = reverse_lazy('users_app:login')

class Recorridos_Sectorial(GlobalMixin, TemplateView):
    template_name = 'home/recorridos_sectorial.html'
    login_url = reverse_lazy('users_app:login')
    
class Error404View(TemplateView):
    template_name = 'home/error404.html'
    

class Error505View(TemplateView):
    template_name = 'home/error404.html'
    
    @classmethod
    def as_error_view(cls):
        v = cls.as_view()
        def view(request):
            r = v(request)
            r.render()
            return r
        return view    
          

    



