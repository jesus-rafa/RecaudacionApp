from django.contrib import admin
from django.db.models.constraints import CheckConstraint

from .models import (CC, CCO, Archivos_Oficios, Archivos_Recibidos,
                     Compartidos, Oficios, Permisos, Recibidos)

admin.site.register(Oficios)
admin.site.register(Permisos)
admin.site.register(Recibidos)
admin.site.register(Compartidos)
admin.site.register(CCO)
admin.site.register(CC)
admin.site.register(Archivos_Recibidos)
admin.site.register(Archivos_Oficios)
