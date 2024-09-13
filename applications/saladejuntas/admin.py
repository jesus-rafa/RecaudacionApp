from django.contrib import admin
from .models import Sala, Categoria, EstatusReuniones, Reuniones, HistoricoReuniones, ParticipantesReuniones, notificacionesCoffeBreak


class CategoriaAdmin(admin.ModelAdmin):
    fields = ["descripcion", "color"]
    list_display = ("descripcion", "color")
    search_fields = ["descripcion"]


class SalasAdmin(admin.ModelAdmin):
    fields = ["descripcion", "detalle_descripcion", "capacidad_sala", "color"]
    list_display = ("descripcion", "color", "capacidad_sala")
    search_fields = ["descripcion"]


class EstatusReunionesAdmin(admin.ModelAdmin):
    fields = ["descripcion"]
    search_fields = ["descripcion"]


class ReunionesAdmin(admin.ModelAdmin):
    list_display = ("evento", "fecha_reunion", "hora_ini_reunion", "hora_fin_reunion", "sala", "is_active")
    list_filter = ["fecha_reunion", "sala", "hora_ini_reunion", "hora_fin_reunion"]
    search_fields = ["fecha_reunion", "evento", "responsable_reunion"]


class ParticipantesReunionesAdmin(admin.ModelAdmin):
    list_display = ("nombre", "reunion_sala_de_juntas", "is_active")
    list_filter = ["reunion_sala_de_juntas"]
    search_fields = ["nombre", "reunion_sala_de_juntas__evento"]


class NotiCoffeBreakAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nombre", "correo", "is_active")


# Register your models here.
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Sala, SalasAdmin)
admin.site.register(EstatusReuniones, EstatusReunionesAdmin)
admin.site.register(Reuniones, ReunionesAdmin)
admin.site.register(HistoricoReuniones)  
admin.site.register(ParticipantesReuniones, ParticipantesReunionesAdmin)
admin.site.register(notificacionesCoffeBreak, NotiCoffeBreakAdmin)
