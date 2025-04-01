# Generated by Django 5.1.7 on 2025-03-30 19:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto_prevencion', '0010_indicador_usuario_medida_proxima_fecha_carga'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indicador',
            name='data',
        ),
        migrations.RemoveField(
            model_name='medida',
            name='datos_requeridos',
        ),
        migrations.CreateModel(
            name='DocumentoRequerido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=255)),
                ('medida', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_requeridos', to='proyecto_prevencion.medida')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentoSubido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='uploads/')),
                ('documento_requerido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyecto_prevencion.documentorequerido')),
                ('indicador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_subidos', to='proyecto_prevencion.indicador')),
            ],
        ),
    ]
