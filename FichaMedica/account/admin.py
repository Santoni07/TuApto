from django.contrib import admin
from .models import Profile
from django.contrib import admin
from .models import Profile
from django.contrib.auth.hashers import make_password
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre', 'apellido', 'dni', 'fecha_nacimiento', 'email', 'rol')  # Campos a mostrar en la lista
    search_fields = ('user__username', 'nombre', 'apellido', 'email')  # Campos por los que se puede buscar
    list_filter = ('rol',)  # Filtros por el rol
    list_editable = ('rol',)  # Permitir edición directa del rol en la lista
    
    def save_model(self, request, obj, form, change):
        # Asegúrate de que el usuario tenga contraseña cifrada
        if obj.user and not obj.user.password.startswith('pbkdf2_'):
            obj.user.password = make_password(obj.user.password)
            obj.user.save()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Personalizar la consulta para incluir información relacionada
        qs = super().get_queryset(request)
        return qs.select_related('user')  # Mejorar el rendimiento al acceder a datos del usuario

admin.site.register(Profile, ProfileAdmin)
