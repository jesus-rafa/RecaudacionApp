# Generated by Django 4.1.6 on 2023-05-25 05:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tramites', '0006_historial_solicitudes_detalle_solicitud_temporal'),
    ]

    operations = [
        migrations.AddField(
            model_name='nuevotramite',
            name='asignar_a',
            field=models.ManyToManyField(blank=True, related_name='Asignar', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='nuevotramite',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
        migrations.AddField(
            model_name='nuevotramite',
            name='linea',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='nuevotramite',
            name='presencial',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
