from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import EstudioCus, Estudiante
from .form import EstudioCusForm   #  Asegurate de tener este form creado
from estudiante.models import Estudiante  # Ajustá si tu modelo de estudiante está en otro lugar
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required



# ✅ CRUD para estudiosCus
@login_required
def seleccionar_estudiante_para_estudio(request):
    estudiantes = Estudiante.objects.all()
    accion = request.GET.get('accion', 'cargar')  # por defecto cargar

    return render(request, 'cus/seleccionar_estudiante_para_estudio.html', {
        'estudiantes': estudiantes,
        'accion': accion
    })
class EstudiosCUSListView(ListView):
    model = EstudioCus
    template_name = 'cus/estudios_list.html'
    context_object_name = 'estudios'

    def get_queryset(self):
        self.estudiante = get_object_or_404(Estudiante, id=self.kwargs['estudiante_id'])
        return EstudioCus.objects.filter(cus__estudiante_id=self.estudiante.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estudiante'] = self.estudiante
        return context


class EliminarEstudioCUSView(DeleteView):
    model = EstudioCus

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        estudiante_id = self.object.cus.estudiante.id

        # Elimina el estudio
        self.object.delete()

        # Agrega mensaje para mostrar en la vista de lista
        messages.success(request, "El estudio fue eliminado correctamente.")
        
        # Redirige a la lista de estudios
        return redirect('listar_estudios', estudiante_id=estudiante_id)

    def get(self, request, *args, **kwargs):
        # Redirige si alguien entra por GET (no permitimos confirmación en página)
        return redirect('listar_estudios', estudiante_id=self.get_object().cus.estudiante.id)

class CargarEstudioCusView(LoginRequiredMixin, CreateView):
    model = EstudioCus
    form_class = EstudioCusForm
    template_name = 'cus/cargar_estudios.html'

    def form_valid(self, form):
        estudiante = get_object_or_404(Estudiante, id=self.kwargs['estudiante_id'])
        cus = estudiante.cus.last()

        if not cus:
            form.add_error(None, "Este estudiante no tiene un CUS asociado.")
            return self.form_invalid(form)

        form.instance.cus = cus
      
        messages.success(self.request, "Estudio cargado con éxito.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estudiante'] = get_object_or_404(Estudiante, id=self.kwargs['estudiante_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('listar_estudios', kwargs={'estudiante_id': self.kwargs['estudiante_id']}) + '?exito=1'