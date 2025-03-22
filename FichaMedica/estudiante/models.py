from django.db import models
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
    
    
    def colegio_activo(self):
        relacion = self.estudiantecolegio_set.filter(activo=True).first()
        return relacion.colegio.nombre if relacion else "Sin colegio"
    def __str__(self):
        return f"{self.nombre} {self.apellido}" if self.tutor and self.tutor.profile else "Estudiante sin perfil"

    
    
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
    
    
class AntecedentesCUS(models.Model):
    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name="antecedentes", null=True, blank=True)

    # 1. VACUNACIONES
    carnet_vacunacion = models.BooleanField(default=False)
    esquema_completo = models.BooleanField(default=False)
    esquema_faltante = models.CharField(max_length=255, blank=True, null=True)

    # 2. ANTECEDENTES PATOLÓGICOS
    enfermedades_importantes = models.TextField(blank=True, null=True)
    cirugias = models.CharField(max_length=255, blank=True, null=True)
    cardiovasculares = models.CharField(max_length=255, blank=True, null=True)
    trauma_funcional = models.CharField(max_length=255, blank=True, null=True)
    alergias= models.CharField(max_length=255, blank=True, null=True)
    oftalmologicos = models.CharField(max_length=255, blank=True, null=True)
    auditivos = models.CharField(max_length=255, blank=True, null=True)
    diabetes = models.BooleanField(default=False)
    asma = models.BooleanField(default=False)
    chagas = models.BooleanField(default=False)
    hipertension = models.BooleanField(default=False)
    neurologico = models.BooleanField(default=False)
    otras= models.CharField(max_length=255, blank=True, null=True)

    # 3. CONDICIONES DE RIESGO
    condiciones_riesgo = models.CharField(max_length=255, blank=True, null=True)

    # 4. MEDICAMENTOS PRESCRIPTOS
    medicamentos_prescriptos = models.CharField(max_length=255, blank=True, null=True)

    # 5. DURANTE ACTIVIDAD FÍSICA PREVIA SUFRIÓ:
    cansancio_extremo = models.BooleanField(default=False)
    falta_aire = models.BooleanField(default=False)
    perdida_conocimiento = models.BooleanField(default=False)
    palpitaciones = models.BooleanField(default=False)
    precordialgias = models.BooleanField(default=False)
    cefaleas = models.BooleanField(default=False)
    vomitos = models.BooleanField(default=False)
    otros = models.CharField(max_length=255, blank=True, null=True)
    # 6 Declaracion jurada 
    declaracion_jurada = models.BooleanField(default=False)
    def __str__(self):
        return f"Antecedentes de {self.estudiante.nombre} {self.estudiante.apellido}" if self.estudiante else "Antecedentes sin asignar"
