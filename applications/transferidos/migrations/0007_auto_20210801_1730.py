# Generated by Django 3.1.4 on 2021-08-01 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferidos', '0006_auto_20210801_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programa_transferidos',
            name='estatus',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Estatus'),
        ),
    ]
