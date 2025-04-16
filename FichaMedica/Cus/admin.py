from django.contrib import admin
from .models import *

@admin.register(Cus)
class CusAdmin(admin.ModelAdmin):
    list_display = ['id', 'estudiante', 'estado', 'fecha_creacion', 'fecha_caducidad']
    list_filter = ['estado', 'fecha_caducidad']
    search_fields = ['estudiante__nombre', 'estudiante__apellido']

@admin.register(ExamenFisico)
class ExamenFisicoAdmin(admin.ModelAdmin):
    list_display = ['cus', 'peso', 'talla', 'imc']

@admin.register(AlimentacionNutricion)
class AlimentacionNutricionAdmin(admin.ModelAdmin):
    list_display = ['cus', 'solicita_plan_especial', 'tipo_plan']

@admin.register(ExamenOftalmologico)
class ExamenOftalmologicoAdmin(admin.ModelAdmin):
    list_display = ['cus', 'agudeza_visual_der', 'agudeza_visual_izq', 'usa_anteojos']

@admin.register(ExamenFonoaudiologico)
class ExamenFonoaudiologicoAdmin(admin.ModelAdmin):
    list_display = ['cus', 'detalles']

@admin.register(ExamenPiel)
class ExamenPielAdmin(admin.ModelAdmin):
    list_display = ['cus', 'detalles']

@admin.register(ExamenOdontologico)
class ExamenOdontologicoAdmin(admin.ModelAdmin):
    list_display = ['cus', 'detalles']

@admin.register(ExamenCardiovascular)
class ExamenCardiovascularAdmin(admin.ModelAdmin):
    list_display = ['cus', 'auscultacion', 'arritmia', 'soplos', 'tension_arterial']

@admin.register(ExamenRespiratorio)
class ExamenRespiratorioAdmin(admin.ModelAdmin):
    list_display = ['cus', 'detalles']

@admin.register(ExamenAbdomen)
class ExamenAbdomenAdmin(admin.ModelAdmin):
    list_display = ['cus', 'detalles']

@admin.register(ExamenGenitourinario)
class ExamenGenitourinarioAdmin(admin.ModelAdmin):
    list_display = ['cus', 'menarca', 'turner']

@admin.register(ExamenEndocrinologico)
class ExamenEndocrinologicoAdmin(admin.ModelAdmin):
    list_display = ['cus', 'detalles']

@admin.register(ExamenOsteoarticular)
class ExamenOsteoarticularAdmin(admin.ModelAdmin):
    list_display = ['cus', 'columna_normal', 'cifosis', 'lordosis', 'escoliosis']

@admin.register(ExamenNeurologico)
class ExamenNeurologicoAdmin(admin.ModelAdmin):
    list_display = ['cus', 'detalles']

@admin.register(EstudioCus)
class EstudioCusAdmin(admin.ModelAdmin):
    list_display = ['cus', 'tipo_estudio', 'fecha_creacion', 'fecha_caducidad']
    list_filter = ['tipo_estudio', 'fecha_caducidad']
    search_fields = ['cus__estudiante__nombre', 'cus__estudiante__apellido']

@admin.register(ComentarioDerivacion)
class ComentarioDerivacionAdmin(admin.ModelAdmin):
    list_display = ['cus', 'comentarios']

@admin.register(Recomendaciones)
class RecomendacionesAdmin(admin.ModelAdmin):
    list_display = ['cus', 'detalles']
@admin.register(ActualizacionCUS)
class ActualizacionCUSAdmin(admin.ModelAdmin):
    list_display = (
        'cus',
        'medico',
        'fecha',
        'vencimiento',
        'lugar',
        'edad',
        'peso',
        'talla',
        'imc',
        'diagnostico_antropometrico',
        'estado_salud_normal',
    )
    list_filter = ('fecha', 'estado_salud_normal')
    search_fields = ('cus__id', 'lugar', 'derivado_a', 'observaciones', 'medico__profile__nombre')
    readonly_fields = ('imc', 'diagnostico_antropometrico', 'fecha')

    fieldsets = (
        (None, {
            'fields': ('cus', 'medico', 'fecha', 'vencimiento','lugar')
        }),
        ('Datos clínicos', {
            'fields': ('edad', 'peso', 'talla', 'imc', 'diagnostico_antropometrico')
        }),
        ('Observaciones', {
            'fields': ('antecedentes', 'examen_fisico', 'estado_salud_normal', 'derivado_a', 'debe_volver', 'observaciones')
        }),
    )
