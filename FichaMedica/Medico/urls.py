from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('medico_home/', MedicoHomeView.as_view(), name='medico_home'),
     # Ruta para el formulario Electro Basal
    path('electro_basal/<int:jugador_id>/', views.electro_basal_view, name='electro_basal_view'),

    # Ruta para el formulario Electro Esfuerzo
    path('electro_esfuerzo/<int:jugador_id>/', views.electro_esfuerzo_view, name='electro_esfuerzo_view'),

    # Ruta para el formulario Cardiovascular
    path('cardiovascular/<int:jugador_id>/', views.cardiovascular_view, name='cardiovascular_view'),

    # Ruta para el formulario Laboratorio
    path('laboratorio/<int:jugador_id>/', views.laboratorio_view, name='laboratorio_view'),

    # Ruta para el formulario Torax
    path('torax/<int:jugador_id>/', views.torax_view, name='torax_view'),

    # Ruta para el formulario Oftalmológico
    path('oftalmologico/<int:jugador_id>/', views.oftalmologico_view, name='oftalmologico_view'),
    # Ruta para el formulario Otros Examenes Clinicos
    path('otros_examenes_clinicos/<int:jugador_id>/', views.otros_examenes_clinicos_view, name='otros_examenes_clinicos_view'),
    # Ruta para el formulario de Registo medico
    path('registro_medico_update/<int:jugador_id>/', views.registro_medico_update_view, name='registro_medico_update_view'),

    path('ficha_medica/<int:jugador_id>/', views.ficha_medica_views, name='ficha_medica'),
    path('eliminar-ficha/<int:jugador_id>/', views.eliminar_ficha_medica, name='eliminar_ficha_medica'),
]
