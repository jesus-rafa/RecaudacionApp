# Generated by Django 3.1.4 on 2021-07-15 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferidos', '0004_auto_20210506_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detalle_transferidos',
            name='estatus',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Estatus'),
        ),
    ]
