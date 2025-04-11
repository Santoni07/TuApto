from django.conf import settings

from django.db import models




class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Permitir múltiples perfiles para un usuario
    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellido = models.CharField(max_length=30, blank=True, null=True)
    dni = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=254)  # Eliminar unique=True para permitir múltiples perfiles con el mismo email

    rol = models.CharField(
        max_length=20,
        choices=[
            ('jugador', 'Jugador'),
            ('medico', 'Médico'),
            ('representante', 'Representante'),
            ('colegio' , 'Colegio'),
            ('estudiante', 'Estudiante'),
        ],
        default='jugador'
    )

    class Meta:
        unique_together = ('user', 'rol')  # Garantiza que un usuario solo tenga un perfil por rol

    @property
    def edad(self):
        from datetime import date
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None

    def save(self, *args, **kwargs):
        # Capitalizar la primera letra del nombre y apellido
        if self.nombre:
            self.nombre = self.nombre.capitalize()
        if self.apellido:
            self.apellido = self.apellido.capitalize()
        
        # Sincronizar el email del Profile con el del User si es necesario
        if self.user and self.user.email != self.email:
            self.user.email = self.email
            self.user.save()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.rol}"