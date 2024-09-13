# Generated by Django 4.1.6 on 2023-05-25 16:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tramites', '0007_nuevotramite_asignar_a_nuevotramite_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='usuario_asignado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuario_asignado_solicitud_tramite', to=settings.AUTH_USER_MODEL),
        ),
    ]
