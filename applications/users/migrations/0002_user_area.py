# Generated by Django 3.1.4 on 2021-03-16 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='area',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
