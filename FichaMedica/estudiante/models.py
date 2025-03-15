""" from django.db import models
from account.models import Profile


class Tutor(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    domicilio = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    localidad = models.CharField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return f"{self.profile.nombre} {self.profile.apellido}"

class Estudiante(models.Model):
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    nombre= models.CharField(max_length=30, blank=True, null=True)
    apellido= models.CharField(max_length=30, blank=True, null=True)
    fecha_nacimiento= models.DateField(blank=True, null=True)
    tutor= models.OneToOneField(Tutor, on_delete=models.CASCADE)
    dni=  models.CharField(max_length=15, blank=True, null=True)
    domicilio = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    sexo=models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True, null=True)
    localidad = models.CharField(max_length=100, blank=True, null=True)
    lugar_nacimiento = models.CharField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return f"{self.profile.nombre} {self.profile.apellido}"
    
class Colegio(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    imagen= models.ImageField(upload_to='colegios/', null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class EstudianteColegio(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    colegio = models.ForeignKey(Colegio, on_delete=models.CASCADE)
    activo= models.BooleanField(default=True)

    def __str__(self):
        return f"{self.estudiante.profile.nombre} {self.estudiante.profile.apellido} - {self.colegio.nombre}"   
    
    

 """