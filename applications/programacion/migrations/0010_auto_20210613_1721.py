# Generated by Django 3.1.4 on 2021-06-13 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0009_auto_20210611_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detalle',
            name='comentarios',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Comentarios'),
        ),
    ]
