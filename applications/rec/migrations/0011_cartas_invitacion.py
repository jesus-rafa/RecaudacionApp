# Generated by Django 3.1.4 on 2021-05-17 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rec', '0010_busquedas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cartas_Invitacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(blank=True, max_length=50, verbose_name='Folio')),
                ('rfc', models.CharField(blank=True, max_length=30, verbose_name='RFC')),
                ('programa', models.CharField(blank=True, max_length=50, null=True, verbose_name='Programa')),
                ('resultado', models.CharField(blank=True, max_length=300, null=True, verbose_name='Nombre')),
                ('fecha_envio', models.DateField(blank=True, null=True, verbose_name='Fecha')),
                ('estatus', models.CharField(blank=True, max_length=50, null=True, verbose_name='Estatus')),
                ('usuario', models.CharField(blank=True, max_length=100, null=True, verbose_name='Usuario')),
            ],
        ),
    ]
