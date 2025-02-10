from django.db import models

class MisNovedades(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='media/novedades')
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha automática al crear

    def __str__(self):
        return self.titulo


class VerSaludBienestar(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='media/salud_bienestar')
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha automática al crear

    def __str__(self):
        return self.titulo