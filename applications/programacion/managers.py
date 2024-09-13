from django.db import models
from django.db.models import Q, F, Count, Sum, When, Case, IntegerField
#from applications.programacion.models import Detalle

class ProgramaManager(models.Manager):
    """ managers para Vigilancia """
        
    def filtrar_seguimiento(self, username):
        list_estatus = ['NUEVO', 'CANCELADA', 'PROPUESTA', 'PRESUNTIVA', 'FAFD', '1-RECHAZADA',
                        '2-RECHAZADA', '3-RECHAZADA', 'OFICIO', 'CONCLUIDO', 'TRANSFERIDO', 'INFORMATIVAS']

        consulta = self.filter(
            detalle_programa__estatus='OFICIO',
            seguimiento__icontains=username
        ).exclude(
            estatus__in=list_estatus
        )

        return consulta
    
    def filtrar_todos(self):
        list_estatus = ['NUEVO','CANCELADA','PROPUESTA','PLAN DE PAGOS','PRESUNTIVA','FAFD','1-RECHAZADA','2-RECHAZADA','3-RECHAZADA','OFICIO','CONCLUIDO','TRANSFERIDO','INFORMATIVAS']

        consulta = self.all().exclude(
            estatus__in = list_estatus
        )

        return consulta

    
        
        
        
        
        
        
        
        
        
        
            




