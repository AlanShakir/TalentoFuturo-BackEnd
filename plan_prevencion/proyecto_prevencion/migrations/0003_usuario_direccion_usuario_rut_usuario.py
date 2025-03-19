# Generated by Django 5.1.5 on 2025-01-24 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto_prevencion', '0002_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='direccion',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='rut_usuario',
            field=models.CharField(blank=True, null=True, unique=True),
        ),
    ]
