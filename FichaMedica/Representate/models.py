from django.db import models
from account.models import Profile
from persona.models import Torneo


class Representante(models.Model):
    
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="representante")  # Relación uno a uno con Profile
    torneo = models.OneToOneField(Torneo, on_delete=models.CASCADE,related_name='representante')  # Relación muchos a muchos con Torneo
    class Meta:
        db_table = 'representante'
        verbose_name = "Representante"
        verbose_name_plural = "Representantes"
    
    
    









 
