from django.contrib import admin
from .models import Programa_Padrones, Detalle_Padrones, Archivos_Padrones, Pagos_Padrones, Programas_Recaudacion

admin.site.register(Programa_Padrones)
admin.site.register(Detalle_Padrones)
admin.site.register(Archivos_Padrones)
admin.site.register(Pagos_Padrones)
admin.site.register(Programas_Recaudacion)



