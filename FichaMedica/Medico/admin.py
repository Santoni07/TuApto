from django.contrib import admin
from .models import Medico

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('profile', 'matricula', 'especialidad', 'telefono_consultorio')
    search_fields = ('profile__nombre', 'profile__apellido', 'especialidad', 'matricula')
    ordering = ('profile__nombre',)