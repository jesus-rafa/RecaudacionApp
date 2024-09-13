# Generated by Django 3.1.4 on 2022-02-08 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_user_jefe_directo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Areas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
                ('clave', models.CharField(blank=True, max_length=100, null=True, verbose_name='Clave')),
                ('is_active', models.BooleanField(default=True)),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='areas', to='users.areas')),
            ],
            options={
                'verbose_name': 'Areas',
                'verbose_name_plural': 'Areas',
                'ordering': ['nombre'],
            },
        ),
    ]
