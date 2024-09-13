from django.db import models
from django.db.models import Q, F, Count, Sum, When, Case, IntegerField

class ProgramaTransferidosManager(models.Manager):
    """ managers para el modelo REC """

    def filtrar(self, **filters):
        
        consulta = self.filter(
            Q(rfc__icontains = filters['kword']) | Q(nombre__icontains = filters['kword'])
        ).filter(
            metodo_envio__icontains=filters['metodo_envio']
        ).filter(
            estatus = filters['estatus']
        ).filter(
            ~Q(usuario=''),
            area = 'EJECUCION',
            is_active = True
        ).order_by('-id')
       
        return consulta

    
    def filtrar_auditoria(self, list, **filters):
        
        consulta = self.filter(
            Q(rfc__icontains = filters['kword']) | Q(nombre__icontains = filters['kword'])
        ).filter(
            metodo_envio__icontains=filters['metodo_envio']
        ).filter(
            estatus__in = list
        ).filter(
            ~Q(usuario=''),
            area = 'AUDITORIA',
            is_active = True
        ).order_by('-id')
       
        return consulta
        
        
        
        
        
        
        
        
        
        
        
            




