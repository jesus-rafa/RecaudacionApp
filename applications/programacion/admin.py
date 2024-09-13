from django.contrib import admin
from .models import Programa, Detalle, Archivos, Pagos, Modelos, Contribuyentes, Impuestos


class ProgramaAdmin(admin.ModelAdmin):
    list_display = ['id','rfc']
    search_fields = ['id']
    
    
class DetalleAdmin(admin.ModelAdmin):
    list_display = ['programa_id_id','etapa','estatus']
    search_fields = ['id']
    
    
admin.site.register(Programa, ProgramaAdmin)
admin.site.register(Detalle, DetalleAdmin)
admin.site.register(Archivos)
admin.site.register(Pagos)
admin.site.register(Modelos)
admin.site.register(Contribuyentes)
admin.site.register(Impuestos)





