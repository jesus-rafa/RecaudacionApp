# Generated by Django 3.1.4 on 2022-02-02 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oficios', '0015_cco_enviado_por'),
    ]

    operations = [
        migrations.AddField(
            model_name='cco',
            name='declinado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cco',
            name='observaciones',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Observaciones'),
        ),
        migrations.AlterField(
            model_name='cco',
            name='enviado_por',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Enviado por'),
        ),
    ]
