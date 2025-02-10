from django.db import models

# Create your models here.

class Publicidad(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='media/publicidades')
    url = models.URLField(blank=True, null=True)  

    def __str__(self):
        return self.titulo