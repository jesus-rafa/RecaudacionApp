# Generated by Django 3.1.4 on 2021-05-17 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('padrones', '0002_auto_20210308_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivos_padrones',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
        migrations.AddField(
            model_name='detalle_padrones',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
        migrations.AddField(
            model_name='pagos_padrones',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
    ]
