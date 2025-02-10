from django.shortcuts import render
from publicidad.models import Publicidad

def home(request):
    publicidades = Publicidad.objects.all()
    return render(request, 'core/home.html', {'publicidades': publicidades})

