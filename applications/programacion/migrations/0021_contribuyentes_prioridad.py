# Generated by Django 3.1.4 on 2022-07-11 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0020_auto_20220711_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='contribuyentes',
            name='prioridad',
            field=models.IntegerField(blank=True, null=True, verbose_name='Prioridad'),
        ),
    ]
