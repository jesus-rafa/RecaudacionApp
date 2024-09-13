from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Accesos, Urls, Plantilla, Areas
    
admin.site.register(User)
admin.site.register(Accesos)
admin.site.register(Urls)
admin.site.register(Plantilla)
admin.site.register(Areas)