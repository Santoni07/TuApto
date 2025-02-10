from django.contrib import admin
from .models import Persona, Jugador, Torneo, Categoria, Equipo, CategoriaEquipo, JugadorCategoriaEquipo

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'direccion', 'telefono', 'telefono_alternativo')
    search_fields = ('profile__nombre', 'profile__apellido')

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('persona_nombre', 'grupo_sanguineo', 'cobertura_medica', 'numero_afiliado')
    search_fields = ('persona__profile__nombre', 'persona__profile__apellido')

    def persona_nombre(self, obj):
        return f"{obj.persona.profile.nombre} {obj.persona.profile.apellido}"
    persona_nombre.short_description = 'Nombre del Jugador'
    
@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen')
    search_fields = ('nombre',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'torneo')
    search_fields = ('nombre',)

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(CategoriaEquipo)
class CategoriaEquipoAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'equipo')
    search_fields = ('categoria__nombre', 'equipo__nombre')

@admin.register(JugadorCategoriaEquipo)
class JugadorCategoriaEquipoAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo_jugador', 'categoria_equipo')

    # Definir un método para obtener el nombre completo del jugador
    def get_nombre_completo_jugador(self, obj):
        return f"{obj.jugador.persona.profile.nombre} {obj.jugador.persona.profile.apellido}"
    
    # Cambiar el nombre que se mostrará en la tabla de administración
    get_nombre_completo_jugador.short_description = 'Jugador'

   
