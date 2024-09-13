from django.db import models
from django.db.models import Case, Count, F, IntegerField, Q, Sum, When


class EventoManager(models.Manager):
    """ managers para Evento """

    def lista_eventos(self):

        consulta = self.filter(
            ~Q(desarrollo_evento=None)
        )

        return consulta


class VisitaManager(models.Manager):
    """ managers para Visita """

    def contribuyentes_por_desarrollo(self, id_desarrollo,username):

        consulta = self.filter(
            id_desarrollo=id_desarrollo,
            #usuario=username,
            is_active=True
        )

        return consulta


class VisitaDetalleManager(models.Manager):
    """ managers para Visita Detalle """

    def tramites_por_contribuyente(self, tramite, idVisita, usuario):
        
        if usuario == '':
            consulta = self.filter(
                id_actividad__tipo_tramite=tramite,
                id_visita=idVisita
            )
        else:
            consulta = self.filter(
                id_actividad__tipo_tramite=tramite,
                id_visita=idVisita,
                usuario=usuario
            )

        # consulta = self.filter(
            # id_actividad__tipo_tramite=tramite,
            # id_visita=idVisita,
            # usuario=usuario
        # )

        return consulta
        
    def tramites_por_contribuyente_todos(self, tramite, rfc):
        
        consulta = self.filter(
            id_actividad__tipo_tramite=tramite,
            id_visita__rfc = rfc
        )

        return consulta

    def get_visita_detalle(self, folio):

        consulta = self.filter(
            folio=folio
        )

        return consulta


class FormularioManager(models.Manager):
    """ managers para Formulario """

    def tipo_formulario_1(self, tramite):

        consulta = self.filter(
            id_actividad__tipo_tramite=tramite,
            tipo_control='checkbox'
        ).order_by('id')

        return consulta
        
    def tipo_formulario_2(self, tramite):

        consulta = self.filter(
            ~Q(tipo_control='checkbox'),
            id_actividad__tipo_tramite=tramite
        ).order_by('id_actividad')

        return consulta
        

    def get_formulario(self, idActividad):

        consulta = self.filter(
            id_actividad=idActividad
        )

        return consulta
