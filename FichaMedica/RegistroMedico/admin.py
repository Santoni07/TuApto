from datetime import timezone
from django.contrib import admin
from .models import (
    AntecedenteEnfermedades, RegistroMedico, EstudiosMedico, ElectroBasal, 
    ElectroEsfuerzo, Cardiovascular, Laboratorio, Torax, Oftalmologico, 
    OtrosExamenesClinicos, EliminacionFichaMedica
)

@admin.register(AntecedenteEnfermedades)
class AntecedenteEnfermedadesAdmin(admin.ModelAdmin):
    list_display = ('id', 'jugador', 'fue_operado', 'toma_medicacion', 'es_diabetico')
    search_fields = ('jugador__persona__nombre', 'jugador__persona__apellido')

@admin.register(RegistroMedico)
class RegistroMedicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'jugador', 'torneo', 'estado', 'fecha_creacion', 'fecha_caducidad')
    list_filter = ('estado', 'torneo')
    search_fields = ('jugador__persona__nombre', 'jugador__persona__apellido', 'torneo__nombre')

@admin.register(EstudiosMedico)
class EstudiosMedicoAdmin(admin.ModelAdmin):
    list_display = ('idestudio', 'jugador', 'tipo_estudio', 'fecha_creacion', 'fecha_caducidad', 'archivo')
    list_filter = ('tipo_estudio', 'fecha_caducidad')
    search_fields = ('jugador__persona__profile__nombre', 'jugador__persona__profile__apellido', 'tipo_estudio')
    ordering = ('-fecha_creacion',)  # Ordenar por fecha más reciente

    def is_expired(self, obj):
        """ Verifica si el estudio está vencido """
        return obj.fecha_caducidad and obj.fecha_caducidad < timezone.now().date()
    
    is_expired.boolean = True
    is_expired.short_description = "Vencido"


@admin.register(ElectroBasal)
class ElectroBasalAdmin(admin.ModelAdmin):
    list_display = ('idelectro_basal', 'ficha_medica', 'ritmo', 'frecuencia', 'observaciones')

@admin.register(ElectroEsfuerzo)
class ElectroEsfuerzoAdmin(admin.ModelAdmin):
    list_display = ('idelectro_esfuerzo', 'ficha_medica', 'observaciones')

@admin.register(Cardiovascular)
class CardiovascularAdmin(admin.ModelAdmin):
    list_display = ('idcardiovascular', 'ficha_medica', 'auscultacion', 'tension_arterial', 'observaciones')

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('idlaboratorio', 'ficha_medica', 'colesterol', 'glucemia', 'otros')

@admin.register(Torax)
class ToraxAdmin(admin.ModelAdmin):
    list_display = ('idtorax', 'ficha_medica', 'observaciones')

@admin.register(Oftalmologico)
class OftalmologicoAdmin(admin.ModelAdmin):
    list_display = ('idoftalmologico', 'ficha_medica', 'od', 'oi')

@admin.register(OtrosExamenesClinicos)
class OtrosExamenesClinicosAdmin(admin.ModelAdmin):
    list_display = ('id', 'ficha_medica', 'respiratorio_observaciones', 'renal_observaciones')

@admin.register(EliminacionFichaMedica)
class EliminacionFichaMedicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'jugador', 'medico', 'fecha_eliminacion')
    list_filter = ('fecha_eliminacion',)
    search_fields = ('jugador', 'medico')
