from django.contrib import admin
from .models import NuevoTramite,Tipos,Tramite,Estatus,Observaciones

admin.site.register(NuevoTramite)
admin.site.register(Tipos)
admin.site.register(Tramite)
admin.site.register(Estatus)
admin.site.register(Observaciones)
