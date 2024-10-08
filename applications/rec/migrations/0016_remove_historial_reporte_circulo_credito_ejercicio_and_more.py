# Generated by Django 4.1.6 on 2023-05-04 18:28
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rec', '0015_rec_notificados'),
    ]

    operations = [
        migrations.CreateModel(
            name='Temporal_Circulo_Credito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rfc', models.CharField(blank=True, max_length=13, null=True, verbose_name='RFC')),
                ('tipo_persona', models.CharField(blank=True, max_length=1, null=True, verbose_name='Tipo Persona')),
                ('numero_cuenta', models.CharField(blank=True, max_length=25, null=True, verbose_name='Número Cuenta')),
                ('razon_social', models.CharField(blank=True, max_length=200, null=True, verbose_name='Razón Social')),
                ('nombre', models.CharField(blank=True, max_length=250, null=True, verbose_name='Nombre')),
                ('apellido_paterno', models.CharField(blank=True, max_length=250, null=True, verbose_name='Apellido Paterno')),
                ('apellido_materno', models.CharField(blank=True, max_length=250, null=True, verbose_name='Apellido Materno')),
                ('curp', models.CharField(blank=True, max_length=18, null=True, verbose_name='CURP')),
                ('fecha_nacimiento', models.CharField(blank=True, max_length=20, null=True, verbose_name='Fecha Nacimiento')),
                ('sexo', models.CharField(blank=True, max_length=1, null=True, verbose_name='Sexo')),
                ('nacionalidad', models.CharField(blank=True, max_length=2, null=True, verbose_name='Nacionalidad')),
                ('calle', models.CharField(blank=True, max_length=60, null=True, verbose_name='Calle')),
                ('numero_ext', models.CharField(blank=True, max_length=30, null=True, verbose_name='Numero ext')),
                ('numero_int', models.CharField(blank=True, max_length=30, null=True, verbose_name='Numero int')),
                ('colonia', models.CharField(blank=True, max_length=40, null=True, verbose_name='Colonia')),
                ('municipio', models.CharField(blank=True, max_length=40, null=True, verbose_name='Municipio')),
                ('ciudad', models.CharField(blank=True, max_length=40, null=True, verbose_name='Ciudad')),
                ('estado', models.CharField(blank=True, max_length=25, null=True, verbose_name='Estado')),
                ('cp', models.CharField(blank=True, max_length=5, null=True, verbose_name='Codigo postal')),
                ('telefono', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefono')),
                ('adeudo', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Adeudo')),
                ('fecha_alta', models.CharField(blank=True, max_length=20, null=True, verbose_name='Fecha Alta')),
                ('fecha_ultimo_pago', models.CharField(blank=True, max_length=20, null=True, verbose_name='Fecha Ultimo Pago')),
                ('correo', models.CharField(blank=True, max_length=250, null=True, verbose_name='Correo Electrónico')),
                ('interlocutor', models.CharField(blank=True, max_length=50, null=True, verbose_name='Interlocutor')),
                ('objeto_contrato', models.CharField(blank=True, max_length=50, null=True, verbose_name='Objeto Contrato')),
                ('clave', models.CharField(blank=True, max_length=4, null=True, verbose_name='Clave')),
                ('sub_clave', models.CharField(blank=True, max_length=4, null=True, verbose_name='Sub Clave')),
                ('importe_baja', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Importe Baja')),
                ('periodo', models.CharField(blank=True, max_length=10, null=True, verbose_name='Periodo')),
                ('ejercicio', models.CharField(blank=True, max_length=10, null=True, verbose_name='Ejercicio')),
                ('descripcion', models.CharField(blank=True, max_length=500, null=True, verbose_name='Descripcion')),
            ],
            options={
                'verbose_name': 'temp_circulo_credito',
                'verbose_name_plural': 'temp_circulo_creditos',
            },
        ),
        migrations.CreateModel(
            name='Circulo_Credito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('rfc', models.CharField(blank=True, max_length=13, null=True, verbose_name='RFC')),
                ('tipo_persona', models.CharField(blank=True, max_length=1, null=True, verbose_name='Tipo Persona')),
                ('numero_cuenta', models.CharField(blank=True, max_length=25, null=True, verbose_name='Número Cuenta')),
                ('razon_social', models.CharField(blank=True, max_length=200, null=True, verbose_name='Razón Social')),
                ('nombre', models.CharField(blank=True, max_length=250, null=True, verbose_name='Nombre')),
                ('apellido_paterno', models.CharField(blank=True, max_length=250, null=True, verbose_name='Apellido Paterno')),
                ('apellido_materno', models.CharField(blank=True, max_length=250, null=True, verbose_name='Apellido Materno')),
                ('curp', models.CharField(blank=True, max_length=18, null=True, verbose_name='CURP')),
                ('fecha_nacimiento', models.DateField(blank=True, null=True, verbose_name='Fecha Nacimiento / Constitución')),
                ('sexo', models.CharField(blank=True, max_length=1, null=True, verbose_name='Sexo')),
                ('nacionalidad', models.CharField(blank=True, max_length=2, null=True, verbose_name='Nacionalidad')),
                ('calle', models.CharField(blank=True, max_length=60, null=True, verbose_name='Calle')),
                ('numero_ext', models.CharField(blank=True, max_length=30, null=True, verbose_name='Numero ext')),
                ('numero_int', models.CharField(blank=True, max_length=30, null=True, verbose_name='Numero int')),
                ('colonia', models.CharField(blank=True, max_length=40, null=True, verbose_name='Colonia')),
                ('municipio', models.CharField(blank=True, max_length=40, null=True, verbose_name='Municipio')),
                ('ciudad', models.CharField(blank=True, max_length=40, null=True, verbose_name='Ciudad')),
                ('estado', models.CharField(blank=True, max_length=25, null=True, verbose_name='Estado')),
                ('cp', models.CharField(blank=True, max_length=5, null=True, verbose_name='Codigo Postal')),
                ('telefono', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefono')),
                ('adeudo', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Adeudo')),
                ('fecha_alta', models.DateField(blank=True, null=True, verbose_name='Fecha Alta')),
                ('fecha_ultimo_pago', models.DateField(blank=True, null=True, verbose_name='Fecha Último Pago')),
                ('correo', models.CharField(blank=True, max_length=250, null=True, verbose_name='Correo Electrónico')),
                ('interlocutor', models.CharField(blank=True, max_length=50, null=True, verbose_name='Interlocutor')),
                ('objeto_contrato', models.CharField(blank=True, max_length=50, null=True, verbose_name='Objeto Contrato')),
                ('clave', models.CharField(blank=True, max_length=4, null=True, verbose_name='Clave')),
                ('sub_clave', models.CharField(blank=True, max_length=4, null=True, verbose_name='Sub Clave')),
                ('importe_baja', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Importe Baja')),
                ('periodo', models.IntegerField(default=0, verbose_name='Periodo')),
                ('ejercicio', models.IntegerField(default=0, verbose_name='Ejercicio')),
                ('usuario', models.CharField(blank=True, max_length=100, null=True, verbose_name='Usuario')),
                ('area', models.CharField(blank=True, max_length=200, null=True, verbose_name='Área')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('descripcion', models.CharField(blank=True, max_length=500, null=True, verbose_name='Descripcion')),
            ],
            options={
                'verbose_name': 'circulo_credito',
                'verbose_name_plural': 'circulo_creditos',
            },
        ),
        migrations.CreateModel(
            name='Historial_Reporte_Circulo_Credito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('accion', models.CharField(max_length=500, verbose_name='Acción')),
                ('periodo', models.IntegerField(default=0, verbose_name='Periodo')),
                ('ejercicio', models.IntegerField(default=0, verbose_name='Ejercicio')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_historial_cc', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historial_Reporte_Circulo_Credito',
                'verbose_name_plural': 'historial_Reportes_Circulo_Credito',
            },
        ),
    ]
