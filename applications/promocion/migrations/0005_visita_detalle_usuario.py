# Generated by Django 3.1.4 on 2021-08-03 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promocion', '0004_desarrollo_responsables'),
    ]

    operations = [
        migrations.AddField(
            model_name='visita_detalle',
            name='usuario',
            field=models.CharField(blank=True, max_length=100, verbose_name='Usuario'),
        ),
    ]
