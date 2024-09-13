from django.contrib import admin
from .models import Codigos_Maestros, Oficinas, Dias_Festivos

admin.site.register(Codigos_Maestros)
admin.site.register(Oficinas)
admin.site.register(Dias_Festivos)
