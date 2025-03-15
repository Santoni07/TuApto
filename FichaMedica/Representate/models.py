from django.db import models
from account.models import Profile
from persona.models import Torneo
""" from estudiante.models import Colegio """


class Representante(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="representante")
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='representantes')  

    class Meta:
        db_table = 'representante'
        verbose_name = "Representante"
        verbose_name_plural = "Representantes"

    def __str__(self):
        return f"{self.profile.nombre} {self.profile.apellido} - {self.torneo.nombre}"

""" 
class RepresenteColegio(models.Model):
    Profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="representante_colegio")
    colegio= models.ForeignKey(Colegio, on_delete=models.CASCADE, related_name='representantes_colegio')

 """




 
