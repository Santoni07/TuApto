from django.contrib import admin
from .models import Publicidad

# Personalización del modelo en el admin
class PublicidadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion', 'url', 'imagen')  # Campos que se mostrarán en el listado
    list_filter = ('titulo',)  # Filtro por título de publicidad
    search_fields = ('titulo', 'descripcion')  # Campos en los que se puede buscar
    ordering = ('titulo',)  # Ordenar las publicidades por título
    readonly_fields = ('url',)  # Hacer solo lectura el campo URL

# Registro del modelo Publicidad en el admin de Django
admin.site.register(Publicidad, PublicidadAdmin)