# Generated by Django 3.1.4 on 2021-03-22 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0004_auto_20210301_2326'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cerrados',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(blank=True, max_length=50, null=True, verbose_name='Folio')),
                ('rfc', models.CharField(blank=True, max_length=30, verbose_name='RFC')),
                ('programa', models.CharField(blank=True, max_length=50, null=True, verbose_name='Programa')),
                ('presuntiva', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Estimado')),
                ('recaudado', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Recaudado')),
                ('dias', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Dias Trasncurridos')),
                ('nombre', models.CharField(blank=True, max_length=200, null=True, verbose_name='Nombre')),
                ('direccion', models.CharField(blank=True, max_length=255, null=True, verbose_name='Direccion')),
                ('fecha', models.DateField(blank=True, null=True, verbose_name='Fecha')),
                ('etapa', models.CharField(blank=True, max_length=50, null=True, verbose_name='Etapa')),
                ('estatus', models.CharField(blank=True, max_length=50, null=True, verbose_name='Estatus')),
                ('seguimiento', models.CharField(blank=True, max_length=100, null=True, verbose_name='Seguimiento')),
                ('usuario', models.CharField(blank=True, max_length=100, null=True, verbose_name='Usuario')),
                ('area', models.CharField(blank=True, max_length=200, null=True, verbose_name='Area')),
            ],
            options={
                'verbose_name': 'Cerrados',
                'verbose_name_plural': 'Cerrados',
                'ordering': ['id'],
            },
        ),
    ]
