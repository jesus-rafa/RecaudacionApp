# Generated by Django 3.1.4 on 2021-06-02 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('padrones', '0004_auto_20210531_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='programa_padrones',
            name='no_control',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='No Control'),
        ),
    ]
