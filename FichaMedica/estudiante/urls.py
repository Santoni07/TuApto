
from django.urls import path
from . import views


urlpatterns = [
   path('menu_estudiante/', views.home_estudiante, name='menu_estudiante'),
   path('cargar_estudiante/', views.cargar_estudiante, name='cargar_estudiante'),
  
   path('listar_estudiantes/', views.listar_estudiantes, name='listar_estudiantes'),
   path('ver_estudiante/', views.ver_estudiante, name='ver_estudiante'),
   path('antecedentes/', views.antecedentes, name='antecedentes')
   


    
]
