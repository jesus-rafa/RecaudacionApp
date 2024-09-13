# Generated by Django 3.1.4 on 2022-01-19 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oficios', '0007_auto_20210301_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='oficios',
            name='comentarios',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Comentarios'),
        ),
        migrations.AddField(
            model_name='recibidos',
            name='pdf_respuesta',
            field=models.FileField(blank=True, null=True, upload_to='media/correspondencia'),
        ),
    ]
