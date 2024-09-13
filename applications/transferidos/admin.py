from django.contrib import admin
from .models import Programa_Transferidos, Detalle_Transferidos, Archivos_Transferidos, Pagos_Transferidos

admin.site.register(Programa_Transferidos)
admin.site.register(Detalle_Transferidos)
admin.site.register(Archivos_Transferidos)
admin.site.register(Pagos_Transferidos)
