from django.urls import path
from .views import *

app_name = 'registroMedico'

urlpatterns = [
    # crud antecedentes medicos 
    path('cargar_antecedente/<int:jugador_id>/', CargarAntecedenteView.as_view(), name='cargar_antecedente'),
    path('ver_antecedente/<int:jugador_id>/', VerAntecedenteView.as_view(), name='ver_antecedente'),
    path('modificar_antecedente/<int:antecedente_id>/', ModificarAntecedenteView.as_view(), name='modificar_antecedente'),
    path('actualizar_consentimiento/<int:pk>/', ActualizarConsentimientoView.as_view(), name='consentimiento'),
    # crud estudios medicos 
    path('cargar_estudio/<int:ficha_id>/', CargarEstudioView.as_view(), name='cargar_estudio'),
    path('ficha/<int:ficha_medica_id>/estudios/', EstudiosMedicoListView.as_view(), name='ver_estudios'),
    path('estudio/<int:pk>/eliminar/', EliminarEstudioView.as_view(), name='eliminar_estudio'),  
    path('estudio/<int:pk>/eliminar/medico/', EliminarEstudioMedicoView.as_view(), name='eliminar_estudio_medico'),
    
]