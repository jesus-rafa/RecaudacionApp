# Generated by Django 4.1.6 on 2023-04-12 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('padrones', '0011_programa_padrones_temporal_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programa_padrones',
            name='is_active',
            field=models.BooleanField(blank=True, default=True, null=True, verbose_name='Activo'),
        ),
    ]
