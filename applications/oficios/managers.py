from datetime import timedelta
from io import UnsupportedOperation

from django.db import models
from django.db.models import Q, F, Value, CharField


class OficiosManager(models.Manager):
    ''' Manager Oficios '''


    def mostrar_oficios(self, list):

        consulta = self.filter(
            usuario__in = list
        )
    
        return consulta


class RecibidosManager(models.Manager):
    ''' Manager Oficios Recibidos '''


    def mostrar_recibidos(self, list):

        consulta = self.filter(
            usuario__in = list
        ).union(self.filter(
            para__in = list
        ))
    
        return consulta


    def recibidos(self, username, copias, turnados, para, user_login): #agregado
        
        if para == 0:
            consulta = self.filter(
                ~Q(para = username),
                estatus__in = ['EN PROCESO','RECHAZADO'],
                usuario = username
            ).annotate(
                tipo=Value("0", CharField())
            ).union(
                self.filter(
                    ~Q(usuario = username),
                    ~Q(pdf = ''),
                    estatus='EN PROCESO',
                    para = username
                ).annotate(
                    tipo=Value("1", CharField())
                )
            ).union(
                self.filter(
                    usuario = username,
                    para = username,
                    estatus='EN PROCESO'
                ).annotate(
                    tipo=Value("2", CharField())
                )
            ).union(
                self.filter(
                    id__in=copias
                ).annotate(
                    tipo=Value("3", CharField())
                )
            ).union(
                self.filter(
                    id__in=turnados
                ).annotate(
                    tipo=Value("4", CharField())
                )
            )
        else:
            consulta = self.filter(
                ~Q(para = username),
                estatus__in = ['EN PROCESO','RECHAZADO'],
                usuario = username,
                para= user_login
            ).annotate(
                tipo=Value("0", CharField())
            ).union(
                self.filter(
                    ~Q(usuario = username),
                    ~Q(pdf = ''),
                    estatus='EN PROCESO',
                    para = username
                ).annotate(
                    tipo=Value("1", CharField())
                )
            ).union(
                self.filter(
                    usuario = username,
                    para = username,
                    estatus='EN PROCESO'
                ).annotate(
                    tipo=Value("2", CharField())
                )
            ).union(
                self.filter(
                    id__in=copias
                ).annotate(
                    tipo=Value("3", CharField())
                )
            ).union(
                self.filter(
                    id__in=turnados
                ).annotate(
                    tipo=Value("4", CharField())
                )
            )

        return consulta


    def recibidos_concluidos(self, username, copias):

        consulta = self.filter(
            ~Q(estatus = 'EN PROCESO'),
            usuario = username
        ).annotate(
            tipo=Value("0", CharField())
        ).union(
            self.filter(
                ~Q(estatus = 'EN PROCESO'),
                para = username
            ).annotate(
                tipo=Value("1", CharField())
            )
        ).union(
            self.filter(
                id__in=copias
            ).annotate(
                tipo=Value("2", CharField())
            )
        )

        return consulta

        