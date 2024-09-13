from django.db import models
from django.db.models import Q, F, Count, Sum, When, Case, IntegerField

class ProgramaManager(models.Manager):
    """ managers para el modelo REC """

    def filtrar(self, **filters):
        
        consulta = self.filter(
            Q(rfc__icontains = filters['kword']) | Q(nombre__icontains = filters['kword'])
        ).filter(
            seguimiento__icontains=filters['user']
        ).filter(
            etapa__icontains=filters['etapa']
        ).filter(
            estatus__icontains=filters['status']
        ).filter(
            programa__icontains=filters['program']
        ).filter(
            area__icontains=filters['area']
        ).exclude(
            estatus = 'CONCLUIDO'
        )

        if filters['top']:
            top = int(filters['top'])
        else:
            top = 0
       
        return consulta[:top]
        
    
    def filtrar_seguimiento(self, username, excluir_programas):

        consulta = self.filter(
            seguimiento__icontains=username
        ).exclude(
            programa__in=excluir_programas,
            etapa='CONCLUIDO',
            estatus='CONCLUIDO'
        )

        return consulta

    def programas_especiales(self, username, programa):

        consulta = self.filter(
            seguimiento__icontains=username,
            programa=programa
        )

        return consulta
        
    def contribuyentes_por_mes(self):
    
        consulta = self.filter(
            ~Q(seguimiento=''),
            ~Q(no_control=''),
            ~Q(no_control=None)
        ).values(
           'no_control'
        ).annotate(
            sum_rfc=Count('rfc'),
            sum_presuntiva=Sum('presuntiva'),
            sum_recaudado=Sum('recaudado'),
            porcentaje=(Sum('recaudado')*100)/Sum('presuntiva')
        ).order_by()
        
        return consulta
        
        
    def detalle_mes(self, no_control):
    
        consulta = self.filter(
            no_control=no_control,
        )
        
        return consulta
        
        
        
        
        
        
        
        
        
        
            




