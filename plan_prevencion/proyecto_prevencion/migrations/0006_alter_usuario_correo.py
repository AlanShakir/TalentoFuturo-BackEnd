# Generated by Django 5.1.5 on 2025-03-05 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto_prevencion', '0005_alter_usuario_rut_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='correo',
            field=models.EmailField(max_length=50),
        ),
    ]
