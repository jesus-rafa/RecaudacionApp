# Generated by Django 3.1.4 on 2021-10-18 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0014_programa_interlocutor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagos',
            name='ejercicio',
            field=models.IntegerField(blank=True, choices=[(2016, '2016'), (2017, '2017'), (2018, '2018'), (2019, '2019'), (2020, '2020'), (2021, '2021')], null=True, verbose_name='Ejercicio'),
        ),
    ]
