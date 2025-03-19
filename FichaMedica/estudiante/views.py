from django.shortcuts import render

# Create your views here.

def home_estudiante(request):
    return render(request, 'estudiante/menu_estudiante.html')  # Asegúrate de que la ruta sea correcta

def cargar_estudiante(request):
    return render(request, 'estudiante/cargar_estudiante.html')

def listar_estudiantes(request):
    return render(request, 'estudiante/listar_estudiantes.html')

def ver_estudiante(request):
    return render(request, 'estudiante/ver_estudiante.html')

def antecedentes(reuest):
    return render(reuest, 'estudiante/antecedentes.html')

def consultar_apto(request):
    return render(request, 'estudiante/consultar_apto.html')