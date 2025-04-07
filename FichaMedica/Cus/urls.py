
from django.urls import path
from .views import *


urlpatterns = [
    path('cus/seleccionar/', seleccionar_estudiante_para_estudio, name='seleccionar_estudiante_para_estudio'),
   path('cargar/<int:estudiante_id>/', CargarEstudioCusView.as_view(), name='cargar_estudio'), 
   path('listar/<int:estudiante_id>/', EstudiosCUSListView.as_view(), name='listar_estudios'),
    path('eliminar/<int:pk>/', EliminarEstudioCUSView.as_view(), name='eliminar_estudio'),
    
]