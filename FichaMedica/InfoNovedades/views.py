from django.shortcuts import render
from .models import MisNovedades,VerSaludBienestar
# Create your views here.


def novedades(request):
    # Obtén todas las novedades de la base de datos
    novedades_list = MisNovedades.objects.all()  
    return render(request, 'novedades/novedades.html', {"novedades": novedades_list})

def salud_bienestar(request):
    salud_bienestar_list = VerSaludBienestar.objects.all()
    return render(request, 'novedades/salud_bienestar.html' ,{"salud_bienestar": salud_bienestar_list})