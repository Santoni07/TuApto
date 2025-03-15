
from django.urls import path
from . import views


urlpatterns = [
   path('menu_estudiante/', views.menu_estudiante, name='menu_estudiante')
    
]
