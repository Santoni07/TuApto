
    
from datetime import datetime, timedelta


from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, DetailView,UpdateView,CreateView,DeleteView,ListView
from .models import RegistroMedico,AntecedenteEnfermedades,EstudiosMedico
from persona.models import JugadorCategoriaEquipo, Jugador
from .forms import AntecedenteEnfermedadesForm,EstudioMedicoForm
from django.contrib.auth.mixins import LoginRequiredMixin

class CargarAntecedenteView(FormView):
    template_name = 'registro_medico/cargar_antecedentes.html'
    form_class = AntecedenteEnfermedadesForm
    success_url = reverse_lazy('menu_jugador')  # Redirige al menú del jugador después de guardar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jugador_id = self.kwargs.get('jugador_id')
        jugador = get_object_or_404(Jugador, id=jugador_id)

        # Obtener el torneo asociado al jugador
        jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(jugador=jugador).first()
        torneo = jugador_categoria_equipo.categoria_equipo.categoria.torneo

        # Añadir información adicional al contexto
        context['jugador'] = jugador
        context['torneo'] = torneo

        # Verificar si ya existe una ficha médica para el jugador y torneo
        ficha_medica, created = RegistroMedico.objects.get_or_create(
            jugador=jugador,
            torneo=torneo,
            defaults={
                'estado': 'PROCESO',
                'fecha_caducidad': datetime.now() + timedelta(days=365)
            }
        )

        # Pasar la ficha médica al contexto
        context['ficha_medica'] = ficha_medica

        return context

    def form_valid(self, form):
        jugador_id = self.kwargs.get('jugador_id')
        jugador = get_object_or_404(Jugador, id=jugador_id)

        # Obtener el torneo asociado al jugador
        jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(jugador=jugador).first()
        torneo = jugador_categoria_equipo.categoria_equipo.categoria.torneo

        # Obtener o crear la ficha médica
        ficha_medica, created = RegistroMedico.objects.get_or_create(
            jugador=jugador,
            torneo=torneo,
            defaults={
                'estado': 'PROCESO',
                'fecha_caducidad': datetime.now() + timedelta(days=365)
            }
        )

        # Guardar el antecedente asociado a la ficha médica
        antecedente = form.save(commit=False)
        antecedente.idfichaMedica = ficha_medica
        antecedente.save()

        return super().form_valid(form)

class VerAntecedenteView(DetailView):
    model = AntecedenteEnfermedades  # Ahora la vista se basa en AntecedenteEnfermedades
    template_name = 'registro_medico/ver_antecedentes.html'
    context_object_name = 'antecedente'  # Se utiliza 'antecedente' para el objeto en la plantilla

    def get_object(self, queryset=None):
        jugador_id = self.kwargs.get('jugador_id')  # Obtener el ID del jugador desde la URL
        jugador = get_object_or_404(Jugador, id=jugador_id)  # Obtener el objeto jugador
        print(jugador)
        # Obtener el torneo asociado al jugador
        jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(jugador=jugador).first()
        torneo = jugador_categoria_equipo.categoria_equipo.categoria.torneo

        # Obtener la ficha médica asociada al jugador y torneo
        ficha_medica = RegistroMedico.objects.filter(jugador=jugador, torneo=torneo).first()

        # Ahora obtener el antecedente usando la ficha médica
        antecedente = get_object_or_404(AntecedenteEnfermedades, idfichaMedica=ficha_medica)
        print(antecedente)
        return antecedente

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        antecedente = self.object  # Obtén el antecedente actual
        profile = self.request.user.profile
        context['profile'] = profile  # Pasar el perfil al contexto
        # Acceso a la ficha médica a través de la relación
        ficha_medica = antecedente.idfichaMedica  
        context['ficha_medica'] = ficha_medica  # Añade la ficha médica al contexto

        return context



class ModificarAntecedenteView(UpdateView):
    model = AntecedenteEnfermedades
    template_name = 'registro_medico/modificar_antecedentes.html'
    form_class = AntecedenteEnfermedadesForm  # Asegúrate de tener el formulario correspondiente
    
    def get_success_url(self):
        # Redirigir a la página de detalle del antecedente, por ejemplo
        return reverse('registroMedico:ver_antecedente', kwargs={'jugador_id': self.object.idfichaMedica.jugador.id})
    def get_object(self, queryset=None):
        # Obtener el ID del antecedente desde la URL
        antecedente_id = self.kwargs.get('antecedente_id')
        # Retornar el objeto AntecedenteEnfermedades correspondiente
        return get_object_or_404(AntecedenteEnfermedades, pk=antecedente_id)



class ActualizarConsentimientoView(UpdateView):
    model = RegistroMedico
    fields = ['consentimiento_persona']  
    template_name = 'registro_medico/consentimiento.html'
    success_url = reverse_lazy('menu_jugador')

    def form_valid(self, form):
        if not form.instance.consentimiento_persona:
            form.instance.consentimiento_persona = True
            form.instance.save()
            print("Consentimiento actualizado a:", form.instance.consentimiento_persona)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el perfil del usuario logueado
        profile = self.request.user.profile
        context['profile'] = profile  # Pasar el perfil al contexto
        
        # Obtener la ficha médica asociada
        ficha_medica = self.get_object()  # Obtiene la instancia actual de RegistroMedico
        context['ficha_medica'] = ficha_medica  # Pasar la ficha médica al contexto
        
        # Obtener el jugador asociado a la ficha médica
        jugador = ficha_medica.jugador  # Aquí asumimos que hay una relación de OneToOne o ForeignKey en RegistroMedico
        context['jugador_info'] = jugador  # Pasar información del jugador al contexto
        
        # Obtener las categorías del equipo
        if jugador:
            # Acceder a las categorías del jugador a través de JugadorCategoriaEquipo
            categorias = JugadorCategoriaEquipo.objects.filter(jugador=jugador)
            context['categorias_equipo'] = categorias  # Pasar las categorías al contexto
        print(f"Ficha médica pk: {ficha_medica.pk}")
        return context

    
    
""" class CargarEstudioView(LoginRequiredMixin, CreateView):
    model = EstudiosMedico
    form_class = EstudioMedicoForm
    template_name = 'registro_medico/cargar_estudios.html'
    success_url = reverse_lazy('menu_jugador')  # Redirige a la lista de estudios tras cargar exitosamente

    def form_valid(self, form):
        # Obtener la ficha médica a partir de la URL o sesión
        ficha_medica = RegistroMedico.objects.get(idfichaMedica=self.kwargs['ficha_id'])

        form.instance.ficha_medica = ficha_medica  # Asocia el estudio a la ficha médica
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ficha_medica'] = get_object_or_404(RegistroMedico, idfichaMedica=self.kwargs['ficha_id'])


        return context 

 """


class CargarEstudioView(LoginRequiredMixin, CreateView):
    model = EstudiosMedico
    form_class = EstudioMedicoForm
    template_name = 'registro_medico/cargar_estudios.html'

    def form_valid(self, form):
        # Obtener la ficha médica a partir de la URL o sesión
        ficha_medica = RegistroMedico.objects.get(idfichaMedica=self.kwargs['ficha_id'])

        form.instance.ficha_medica = ficha_medica  # Asocia el estudio a la ficha médica
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ficha_medica'] = get_object_or_404(RegistroMedico, idfichaMedica=self.kwargs['ficha_id'])
        return context

    def get_success_url(self):
        # Cambiar al nombre correcto del patrón de URL
        return reverse_lazy('registroMedico:ver_estudios', kwargs={'ficha_medica_id': self.kwargs['ficha_id']})

class EstudiosMedicoListView(ListView):
    model = EstudiosMedico
    template_name = 'registro_medico/estudios_list.html'  # Ruta del template
    context_object_name = 'estudios'

    # Filtrar los estudios por ficha médica
    def get_queryset(self):
        ficha_medica_id = self.kwargs.get('ficha_medica_id')
        return EstudiosMedico.objects.filter(ficha_medica__idfichaMedica=ficha_medica_id)

class EliminarEstudioView(DeleteView):
    model= EstudiosMedico
    template_name = 'registro_medico/eliminar_estudio_confirm.html'
    context_object_name = 'estudio' 
    def get_success_url(self):
       ficha_medica_id = self.object.ficha_medica.idfichaMedica
       return reverse_lazy('registroMedico:ver_estudios', kwargs={'ficha_medica_id': ficha_medica_id})

class EliminarEstudioMedicoView(DeleteView):
    model = EstudiosMedico
    template_name = 'registro_medico/eliminar_estudio_confirm.html'
    success_url = reverse_lazy('medico_home')  # Redirige a la lista de estudios

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ficha_medica'] = self.object.ficha_medica  # Agrega la ficha médica al contexto
        return context