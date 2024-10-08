# Generated by Django 3.1.4 on 2022-07-18 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0030_impuestos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='impuestos',
            name='ejericio',
            field=models.IntegerField(blank=True, verbose_name='año actual'),
        ),
        migrations.AlterField(
            model_name='impuestos',
            name='ejericio_1',
            field=models.IntegerField(blank=True, verbose_name='año -1'),
        ),
        migrations.AlterField(
            model_name='impuestos',
            name='ejericio_2',
            field=models.IntegerField(blank=True, verbose_name='año -2'),
        ),
        migrations.AlterField(
            model_name='impuestos',
            name='ejericio_3',
            field=models.IntegerField(blank=True, verbose_name='año -3'),
        ),
        migrations.AlterField(
            model_name='impuestos',
            name='ejericio_4',
            field=models.IntegerField(blank=True, verbose_name='año -4'),
        ),
        migrations.AlterField(
            model_name='impuestos',
            name='ejericio_5',
            field=models.IntegerField(blank=True, verbose_name='año -5'),
        ),
    ]
