# Generated by Django 3.1.4 on 2023-01-19 22:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0016_auto_20220301_1123'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('descripcion', models.CharField(max_length=255, verbose_name='Descripción')),
                ('color', models.CharField(max_length=255, verbose_name='Color')),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='EstatusReuniones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('descripcion', models.CharField(max_length=255, verbose_name='Descripcion')),
            ],
            options={
                'verbose_name': 'Estatus Reuniones',
                'verbose_name_plural': 'Estatus Reuniones',
            },
        ),
        migrations.CreateModel(
            name='notificacionesCoffeBreak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('nombre', models.CharField(blank=True, max_length=500, null=True, verbose_name='Nombre')),
                ('correo', models.CharField(blank=True, max_length=500, null=True, verbose_name='Correo')),
                ('is_active', models.BooleanField(default=True, verbose_name='Registro Activo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_notificaciones_coffe_break', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notificación Coffe Break',
                'verbose_name_plural': 'Notificaciones Coffe Break',
            },
        ),
        migrations.CreateModel(
            name='Sala',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('descripcion', models.CharField(max_length=255, verbose_name='Nombre')),
                ('capacidad_sala', models.IntegerField(verbose_name='Número máximo de personas')),
                ('calendario_id', models.CharField(blank=True, max_length=500, null=True, verbose_name='Calendario id')),
                ('color', models.CharField(blank=True, max_length=255, null=True, verbose_name='Color')),
            ],
            options={
                'verbose_name': 'Sala',
                'verbose_name_plural': 'Salas',
            },
        ),
        migrations.CreateModel(
            name='Reuniones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evento_id', models.CharField(blank=True, max_length=500, null=True, verbose_name='Evento')),
                ('descripcion_evento', models.CharField(blank=True, max_length=500, null=True, verbose_name='Descripción Evento')),
                ('evento', models.CharField(blank=True, max_length=255, null=True, verbose_name='Evento')),
                ('fecha_reunion', models.DateField(verbose_name='Fecha Reunión')),
                ('hora_ini_reunion', models.CharField(max_length=5, verbose_name='Hora Inicio')),
                ('hora_fin_reunion', models.CharField(max_length=5, verbose_name='Hora Fin')),
                ('tiempo', models.IntegerField(default=0, verbose_name='Tiempo')),
                ('is_active', models.BooleanField(default=True, verbose_name='Registro Activo')),
                ('requiere_coffe_break', models.BooleanField(default=False, verbose_name='Requiere Coffe Break')),
                ('tiempo_coffe_break', models.IntegerField(default=0, verbose_name='Tiempo Coffe Break')),
                ('responsable_reunion', models.CharField(max_length=500, verbose_name='Responsable')),
                ('detalles_coffe_break', models.CharField(blank=True, max_length=500, null=True, verbose_name='Detalles')),
                ('total_participantes', models.IntegerField(default=0, verbose_name='Total Personas')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='area_sala_de_juntas', to='users.areas')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reunion_sala_de_juntas', to='saladejuntas.categoria')),
                ('estatus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estatus_sala_de_juntas', to='saladejuntas.estatusreuniones')),
                ('sala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sala_sala_de_juntas', to='saladejuntas.sala')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_sala_de_juntas', to=settings.AUTH_USER_MODEL)),
                ('usuario_noti_coffe_break', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones_coffe_break_reuniones', to='saladejuntas.notificacionescoffebreak')),
                ('usuario_responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuario_responsable_reunion', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reunión',
                'verbose_name_plural': 'Reuniones',
            },
        ),
        migrations.CreateModel(
            name='ParticipantesReuniones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('correo', models.CharField(max_length=255, verbose_name='Correo Electrónico')),
                ('nombre', models.CharField(max_length=255, verbose_name='Participante')),
                ('is_active', models.BooleanField(default=True, verbose_name='Registro Activo')),
                ('reunion_sala_de_juntas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participantes_sala_de_juntas', to='saladejuntas.reuniones')),
            ],
            options={
                'verbose_name': 'Participantes Reuniones',
                'verbose_name_plural': 'Participantes Reuniones',
            },
        ),
        migrations.CreateModel(
            name='HistoricoReuniones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('descripcion', models.CharField(max_length=500, verbose_name='Acción')),
                ('estatus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hist_estatus_sala_de_juntas', to='saladejuntas.estatusreuniones')),
                ('reunion_sala_de_juntas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico_sala_de_juntas', to='saladejuntas.reuniones')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_historico_sala_de_juntas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Histórico Reuniones',
                'verbose_name_plural': 'Histórico Reuniones',
            },
        ),
    ]
