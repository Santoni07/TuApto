from django.shortcuts import render

# Create your views here.

def home_estudiante(request):
    return render(request, 'estudiante/menu_estudiante.html')  # Asegúrate de que la ruta sea correcta