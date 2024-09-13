# Generated by Django 3.1.4 on 2022-02-03 17:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oficios', '0017_cco_tipo'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cco',
            unique_together={('oficio', 'user', 'enviado_por')},
        ),
    ]
