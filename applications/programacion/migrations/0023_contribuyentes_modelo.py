# Generated by Django 3.1.4 on 2022-07-14 14:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0022_contribuyentes_is_ready'),
    ]

    operations = [
        migrations.AddField(
            model_name='contribuyentes',
            name='modelo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='contribuyentes_modelo', to='programacion.modelos'),
            preserve_default=False,
        ),
    ]
