# Generated by Django 3.1.4 on 2021-09-08 23:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20210801_1246'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plantilla',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orientacion', models.IntegerField(default=0, verbose_name='Orientacion')),
                ('barra', models.IntegerField(default=0, verbose_name='Barra')),
                ('menu', models.IntegerField(default=0, verbose_name='Menu')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plantilla', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Plantilla',
                'verbose_name_plural': 'Plantilla',
                'ordering': ['user'],
            },
        ),
    ]
