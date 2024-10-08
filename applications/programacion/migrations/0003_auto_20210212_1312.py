# Generated by Django 3.1.4 on 2021-02-12 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0002_pagos_presuntiva'),
    ]

    operations = [
        migrations.AddField(
            model_name='programa',
            name='dias',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Dias Trasncurridos'),
        ),
        migrations.AddField(
            model_name='programa',
            name='folio',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Folio'),
        ),
        migrations.AddField(
            model_name='programa',
            name='recaudado',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Recaudado'),
        ),
        migrations.AlterField(
            model_name='pagos',
            name='accesorios',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Accesorios'),
        ),
        migrations.AlterField(
            model_name='pagos',
            name='impuesto',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Impuesto'),
        ),
        migrations.AlterField(
            model_name='pagos',
            name='recargos',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Recargos'),
        ),
    ]
