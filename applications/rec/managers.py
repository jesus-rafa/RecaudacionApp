from django.db import models
from django.db.models import Q, F, Count, Sum, When, Case, IntegerField

class RECManager(models.Manager):
    """ managers para el modelo REC """

    def buscar_rfc(self, kword):

        if kword == '':
            return self.none()
        else:
            consulta = self.filter(
                Q(rfc__icontains = kword) | Q(nombre__icontains = kword)
            ).annotate(
                num_contacs=Sum(
                    Case(When(contacto__visible = True, then=1),  
                        When(contacto__visible = False), then=0),
                        output_field=IntegerField()
                      
                )
            )

            return consulta





    def contacto_all(self, kword):

        resultado = self.filter(
            rfc = kword
        )

        return resultado




class ContactoManager(models.Manager):
    """ managers para el modelo Contacto """

    def detalle_all_visible(self, kword):

        resultado = self.filter(
            rfc = kword, visible = True, is_active=True
        ).order_by('-fecha_alta')

        return resultado

    
    def detalle_all(self, kword):

        resultado = self.filter(
            rfc = kword,
            is_active=True
        )

        return resultado


    
    # def numero_contactos(self, kword):
        
    #     consulta = self.filter(
    #        count = kword
    #     )
        
    #     return consulta

