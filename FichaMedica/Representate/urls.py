from django.urls import path
from .views import RepresentanteHomeView,TraerEquiposPorCategorias
from . import views

urlpatterns = [
   path('representante-home/', RepresentanteHomeView.as_view(), name='representante_home'),
   path('ajax/traer-equipos/',TraerEquiposPorCategorias.as_view(), name='traer_equipos')
   
   
]