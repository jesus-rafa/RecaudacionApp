from django.contrib import admin

from .models import (Actividades, Desarrollo, Evento, Formulario, Opciones,
                     Participantes, Programa_Actualizaciones, Visita,
                     Visita_Detalle, Detalle)

admin.site.register(Programa_Actualizaciones)
admin.site.register(Evento)
admin.site.register(Desarrollo)
admin.site.register(Participantes)
admin.site.register(Actividades)
admin.site.register(Formulario)
admin.site.register(Visita)
admin.site.register(Visita_Detalle)
admin.site.register(Opciones)
admin.site.register(Detalle)
