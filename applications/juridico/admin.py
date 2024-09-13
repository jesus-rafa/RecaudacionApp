from django.contrib import admin
from .models import Catalogo, Demanda, Formulario, Rubros, Archivos_Juridico, Proceso_Detalle, Solicitante, Resolutor,Resolutor_detalle, Requisitos 
# Register your models here.
admin.site.register(Demanda)
admin.site.register(Catalogo)
#admin.site.register(Mouse)
# admin.site.register(Procesal_Detalle)
admin.site.register(Formulario)
admin.site.register(Rubros)
admin.site.register(Archivos_Juridico)
admin.site.register(Proceso_Detalle)
admin.site.register(Solicitante)
admin.site.register(Resolutor)
admin.site.register(Resolutor_detalle)
admin.site.register(Requisitos)