from django.contrib import admin
from .models import Tutor, Estudiante, Colegio, EstudianteColegio,AntecedentesCUS

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('profile', 'domicilio', 'telefono', 'localidad')
    search_fields = ('profile__nombre', 'profile__apellido', 'telefono', 'localidad')
    list_filter = ('localidad',)

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'tutor', 'fecha_nacimiento', 'localidad')
    search_fields = ('nombre', 'apellido', 'dni')
    list_filter = ('sexo', 'localidad')
    autocomplete_fields = ['tutor']

@admin.register(Colegio)
class ColegioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono')
    search_fields = ('nombre', 'direccion')

@admin.register(EstudianteColegio)
class EstudianteColegioAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'colegio', 'activo')
    list_filter = ('activo', 'colegio')
    search_fields = ('estudiante__nombre', 'estudiante__apellido', 'colegio__nombre')
    autocomplete_fields = ['estudiante', 'colegio']

@admin.register(AntecedentesCUS)
class AntecedentesCUSAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "carnet_vacunacion", "esquema_completo", "condiciones_riesgo", "medicamentos_prescriptos")
    list_filter = ("carnet_vacunacion", "esquema_completo", "condiciones_riesgo")
    search_fields = ("estudiante__nombre", "estudiante__apellido", "enfermedades_importantes", "medicamentos_prescriptos")
    readonly_fields = ("estudiante",)  # Para evitar que se edite directamente en admin

    fieldsets = (
        ("Datos del Estudiante", {
            "fields": ("estudiante",)
        }),
        ("Vacunaciones", {
            "fields": ("carnet_vacunacion", "esquema_completo", "esquema_faltante")
        }),
        ("Antecedentes Patológicos", {
            "fields": ("enfermedades_importantes", "cirugias", "cardiovasculares", "trauma_funcional")
        }),
        ("Condiciones de Riesgo y Medicación", {
            "fields": ("condiciones_riesgo", "medicamentos_prescriptos")
        }),
        ("Durante Actividad Física Previa Sufrió", {
            "fields": ("cansancio_extremo", "falta_aire", "perdida_conocimiento", "palpitaciones", "precordialgias", "cefaleas", "vomitos", "otros")
        }),
    )

    def get_queryset(self, request):
        """Optimiza la consulta usando `select_related` para mejorar el rendimiento."""
        return super().get_queryset(request).select_related("estudiante")