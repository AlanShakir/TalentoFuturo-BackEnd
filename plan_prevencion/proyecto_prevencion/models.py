from django.contrib.auth.models import AbstractUser
from django.db import models

class OrganismoPublico(models.Model):
    nombre_organismo = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_organismo
    
class ComunaPlan(models.Model):
    nombre_comuna = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_comuna

class TiposMedidas(models.Model):
    nombre_tipo_medida = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_tipo_medida

class Medida(models.Model):
    TIPO_FORMULA_CHOICES = [
        ('Formula', 'Formula'),
        ('Dicotomica', 'Dicotómica'),
        ('Numero', 'Número'),
    ]

    FRECUENCIA_CHOICES = [
        ('anual', 'Anual'),
        ('unica', 'Única'),
    ]

    tipo_medida = models.ForeignKey(TiposMedidas, on_delete=models.CASCADE,null=True, blank=True)
    nombre_corto = models.CharField(max_length=255)
    nombre_largo = models.CharField(max_length=255)
    organismo = models.ForeignKey(OrganismoPublico, on_delete=models.CASCADE)
    comunas = models.ForeignKey(ComunaPlan, on_delete=models.CASCADE)
    regulatorio = models.BooleanField(default=True)
    descripcion_formula = models.TextField()
    tipo_formula = models.CharField(max_length=20, choices=TIPO_FORMULA_CHOICES)
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIA_CHOICES)
    proxima_fecha_carga = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_corto
    
class DocumentoRequerido(models.Model):
    medida = models.ForeignKey(Medida, on_delete=models.CASCADE, related_name="documentos_requeridos")
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return self.descripcion

class Usuario(AbstractUser):
    rut_usuario = models.CharField(unique=True, blank=True, null=True, max_length=10)
    organismo = models.ForeignKey(OrganismoPublico, blank=True, null=True, on_delete=models.CASCADE)
    aprobado = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.username
    
class Indicador(models.Model):
    medida = models.ForeignKey(Medida, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    calculo_indicador = models.FloatField()
    cumple_requisitos = models.BooleanField(default=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_rechazo = models.DateTimeField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
    motivo_rechazo = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"Indicador para {self.medida.nombre_corto}"
    
class DocumentoSubido(models.Model):
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, related_name="documentos_subidos")
    documento_requerido = models.ForeignKey(DocumentoRequerido, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"{self.documento_requerido.descripcion} para {self.indicador.medida.nombre_corto}"
