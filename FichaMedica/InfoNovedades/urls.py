from django.urls import path
from .import views



urlpatterns = [
    path('InfoNovedades/', views.novedades, name='novedades'),  # Ruta para novedades
    path('SaludBienestar/', views.salud_bienestar, name='salud_bienestar'),  # Ruta para salud y bienestar
]
