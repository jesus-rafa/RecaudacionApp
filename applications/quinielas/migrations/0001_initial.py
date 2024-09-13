# Generated by Django 3.1.4 on 2022-11-17 19:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True, verbose_name='Nombre')),
                ('logo', models.CharField(blank=True, max_length=600, null=True, verbose_name='Logo')),
            ],
            options={
                'verbose_name': 'Equipo',
                'verbose_name_plural': 'Equipos',
            },
        ),
        migrations.CreateModel(
            name='Partidos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('fecha_hora', models.DateTimeField(verbose_name='Fecha y Hora')),
                ('resultado_local', models.IntegerField(default=0, verbose_name='Resultado Local')),
                ('resultado_visitante', models.IntegerField(default=0, verbose_name='Resultado Visitante')),
                ('ganador', models.IntegerField(default=0, verbose_name='Ganador')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='local_equipos', to='quinielas.equipos')),
                ('visitante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitantes_equipos', to='quinielas.equipos')),
            ],
            options={
                'verbose_name': 'Partido',
                'verbose_name_plural': 'Partidos',
            },
        ),
        migrations.CreateModel(
            name='Pronostico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('pronostico', models.IntegerField(default=0, verbose_name='Pronóstico')),
                ('puntos', models.IntegerField(default=0, verbose_name='Puntos')),
                ('pronostico_local', models.IntegerField(default=0, verbose_name='Resultado Local')),
                ('pronostico_visitante', models.IntegerField(default=0, verbose_name='Resultado Visitante')),
                ('partido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pronostico_partido', to='quinielas.partidos')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Pronostico',
                'verbose_name_plural': 'Pronosticos',
            },
        ),
    ]
