# Generated by Django 3.1.4 on 2022-02-09 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oficios', '0019_auto_20220208_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='recibidos',
            name='cc_externas',
            field=models.CharField(blank=True, max_length=254, null=True, verbose_name='CC Externas'),
        ),
    ]
