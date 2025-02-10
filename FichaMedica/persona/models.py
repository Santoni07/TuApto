from django.db import models
from account.models import Profile  # Asegúrate de ajustar la ruta según tu estructura

class Persona(models.Model):
    

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    telefono_alternativo = models.CharField(max_length=15, blank=True, null=True)
   
   

    def __str__(self):
        return f"{self.profile.nombre} {self.profile.apellido}"

class Jugador(models.Model):
    GRUPOS_SANGUINEOS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
    grupo_sanguineo = models.CharField(max_length=3, choices=GRUPOS_SANGUINEOS, blank=True, null=True)  
    cobertura_medica = models.CharField(max_length=100, blank=True, null=True)
    numero_afiliado = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
       
        return f"{self.persona.profile.nombre} {self.persona.profile.apellido}"

class Torneo(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción',null=True, blank=True)
    direccion = models.CharField(max_length=255, verbose_name='Dirección', null=True, blank=True)
    telefono = models.CharField(max_length=15, verbose_name='Teléfono', null=True, blank=True)
    imagen = models.ImageField(upload_to='imagenes/', null=True, blank=True, verbose_name='Imagen')
    
    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=45)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='categorias')

    class Meta:
        db_table = 'categorias'  # Nombre de la tabla en la base de datos

    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    nombre = models.CharField(max_length=45)

    class Meta:
        db_table = 'equipo'  # Nombre de la tabla en la base de datos

    def __str__(self):
        return self.nombre


class CategoriaEquipo(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='categoria_equipos')
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='categoria_equipos')

    class Meta:
        db_table = 'categoria_equipo'
        unique_together = ('categoria', 'equipo')

    def __str__(self):
        return f"{self.categoria.nombre} - {self.equipo.nombre} - {self.categoria.torneo}"


class JugadorCategoriaEquipo(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    categoria_equipo = models.ForeignKey(CategoriaEquipo, on_delete=models.CASCADE, related_name='jugadores')

    class Meta:
        db_table = 'jugador_categoria_equipo'
   
    def __str__(self):
        return f"{self.jugador.persona.profile.nombre} {self.jugador.persona.profile.apellido} - {self.categoria_equipo.equipo.nombre} - {self.categoria_equipo.categoria.nombre} - {self.categoria_equipo.categoria.torneo}"

