# Generated by Django 3.1.4 on 2022-08-18 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('juridico', '0002_auto_20220621_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='proceso',
            name='fecha_aviso',
            field=models.DateField(blank=True, null=True, verbose_name='proceso_aviso'),
        ),
        migrations.AddField(
            model_name='proceso',
            name='fecha_notificacion',
            field=models.DateField(blank=True, null=True, verbose_name='proceso_notificacion'),
        ),
    ]
