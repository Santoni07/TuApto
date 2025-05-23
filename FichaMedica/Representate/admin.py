from django.contrib import admin

# Register your models here.

from .models import *

@admin.register(Representante)
class RepresentanteAdmin(admin.ModelAdmin):
    list_display = ('profile', 'torneo')
    list_filter = ('profile', 'torneo')
    search_fields = ('profile__user__username', 'torneo__nombre')
    
    
@admin.register(RepresenteColegio)
class RepresenteColegioAdmin(admin.ModelAdmin):
    list_display = ('Profile', 'colegio')
    list_filter = ('Profile', 'colegio')
    