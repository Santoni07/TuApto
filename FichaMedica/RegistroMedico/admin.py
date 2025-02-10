from django.contrib import admin
from django.utils.html import format_html
from .models import *

# Registro de AntecedenteEnfermedades en el admin
@admin.register(AntecedenteEnfermedades)
class AntecedenteEnfermedadesAdmin(admin.ModelAdmin):
    list_display = ('idantecedente_enfermedades', 'get_jugador', 'fue_operado', 'toma_medicacion', 'es_diabetico', 'es_amatico')
    search_fields = ('idantecedente_enfermedades',)
    list_filter = ('fue_operado', 'toma_medicacion', 'es_diabetico', 'es_amatico')

    def get_jugador(self, obj):
        # Accede al jugador a través de la ficha médica
        return f"{obj.idfichaMedica.jugador.persona.profile.nombre} {obj.idfichaMedica.jugador.persona.profile.apellido}"
    
    get_jugador.short_description = 'Jugador'


# Registro de RegistroMedico en el admin
@admin.register(RegistroMedico)
class RegistroMedicoAdmin(admin.ModelAdmin):
    list_display = ('idfichaMedica', 'jugador', 'torneo', 'estado', 'fecha_creacion', 'fecha_caducidad','consentimiento_persona')
    search_fields = ('idfichaMedica', 'jugador__nombre', 'torneo__nombre')
    list_filter = ('estado', 'torneo', 'fecha_creacion')
    # Agrega más filtros o campos de búsqueda según tu necesidad
# Personalización de EstudiosMedico en el admin
@admin.register(EstudiosMedico)
class EstudiosMedicoAdmin(admin.ModelAdmin):
    list_display = ('idestudio', 'get_jugador', 'tipo_estudio', 'archivo', 'observaciones')
    search_fields = ('idestudio', 'ficha_medica__jugador__persona__profile__nombre', 'tipo_estudio')
    list_filter = ('tipo_estudio',)

    def get_jugador(self, obj):
        return f"{obj.ficha_medica.jugador.persona.profile.nombre} {obj.ficha_medica.jugador.persona.profile.apellido}"
    get_jugador.short_description = 'Jugador'

# Personalización de ElectroBasal en el admin
@admin.register(ElectroBasal)
class ElectroBasalAdmin(admin.ModelAdmin):
    list_display = ('idelectro_basal', 'get_jugador', 'ritmo', 'PQ', 'frecuencia', 'arritmias', 'ejeQRS', 'trazadoNormal', 'observaciones')
    search_fields = ('idelectro_basal', 'ficha_medica__jugador__persona__profile__nombre')
    
    def get_jugador(self, obj):
        return f"{obj.ficha_medica.jugador.persona.profile.nombre} {obj.ficha_medica.jugador.persona.profile.apellido}"
    get_jugador.short_description = 'Jugador'

# Personalización de ElectroEsfuerzo en el admin
@admin.register(ElectroEsfuerzo)
class ElectroEsfuerzoAdmin(admin.ModelAdmin):
    list_display = ('idelectro_esfuerzo', 'get_jugador', 'observaciones')
    search_fields = ('idelectro_esfuerzo', 'ficha_medica__jugador__persona__profile__nombre')

    def get_jugador(self, obj):
        return f"{obj.ficha_medica.jugador.persona.profile.nombre} {obj.ficha_medica.jugador.persona.profile.apellido}"
    get_jugador.short_description = 'Jugador'

# Personalización de Cardiovascular en el admin
@admin.register(Cardiovascular)
class CardiovascularAdmin(admin.ModelAdmin):
    list_display = ('idcardiovascular', 'get_jugador', 'auscultacion', 'soplos', 'tension_arterial', 'ruidos_agregados', 'observaciones')
    search_fields = ('idcardiovascular', 'ficha_medica__jugador__persona__profile__nombre')

    def get_jugador(self, obj):
        return f"{obj.ficha_medica.jugador.persona.profile.nombre} {obj.ficha_medica.jugador.persona.profile.apellido}"
    get_jugador.short_description = 'Jugador'

# Personalización de Laboratorio en el admin
@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('idlaboratorio', 'get_jugador', 'citologico', 'orina', 'colesterol', 'uremia', 'glucemia', 'otros')
    search_fields = ('idlaboratorio', 'ficha_medica__jugador__persona__profile__nombre')

    def get_jugador(self, obj):
        return f"{obj.ficha_medica.jugador.persona.profile.nombre} {obj.ficha_medica.jugador.persona.profile.apellido}"
    get_jugador.short_description = 'Jugador'

# Personalización de Torax en el admin
@admin.register(Torax)
class ToraxAdmin(admin.ModelAdmin):
    list_display = ('idtorax', 'get_jugador', 'observaciones')
    search_fields = ('idtorax', 'ficha_medica__jugador__persona__profile__nombre')

    def get_jugador(self, obj):
        return f"{obj.ficha_medica.jugador.persona.profile.nombre} {obj.ficha_medica.jugador.persona.profile.apellido}"
    get_jugador.short_description = 'Jugador'

# Personalización de Oftalmologico en el admin
@admin.register(Oftalmologico)
class OftalmologicoAdmin(admin.ModelAdmin):
    list_display = ('idoftalmologico', 'get_jugador', 'od', 'oi')
    search_fields = ('idoftalmologico', 'ficha_medica__jugador__persona__profile__nombre')

    def get_jugador(self, obj):
        return f"{obj.ficha_medica.jugador.persona.profile.nombre} {obj.ficha_medica.jugador.persona.profile.apellido}"
    get_jugador.short_description = 'Jugador'
    
@admin.register(EliminacionFichaMedica)
class EliminacionFichaMedicaAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'medico', 'fecha_eliminacion')  # Campos visibles en la lista
    search_fields = ('jugador', 'medico')  # Agrega una barra de búsqueda
    list_filter = ('fecha_eliminacion',)  # Permite filtrar por fecha de eliminación
    ordering = ('-fecha_eliminacion',)  # Ordena por la eliminación más reciente primero