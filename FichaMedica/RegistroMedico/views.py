
    
from datetime import datetime, timedelta


from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, DetailView,UpdateView,CreateView,DeleteView,ListView
from .models import RegistroMedico,AntecedenteEnfermedades,EstudiosMedico
from persona.models import JugadorCategoriaEquipo, Jugador
from .forms import AntecedenteEnfermedadesForm,EstudioMedicoForm
from django.contrib.auth.mixins import LoginRequiredMixin
from account.models import Profile

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
                
            }
        )

        # Pasar la ficha médica al contexto
        context['ficha_medica'] = ficha_medica

        return context

    def form_valid(self, form):
        jugador_id = self.kwargs.get('jugador_id')
        jugador = get_object_or_404(Jugador, id=jugador_id)
        print(f"Jugador encontrado: {jugador}")  # Depuración
        # Obtener el torneo asociado al jugador
        jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(jugador=jugador).first()
        torneo = jugador_categoria_equipo.categoria_equipo.categoria.torneo

        # Obtener o crear la ficha médica
        ficha_medica, created = RegistroMedico.objects.get_or_create(
            jugador=jugador,
            torneo=torneo,
            defaults={
                'estado': 'PROCESO',
                'fecha_caducidad': datetime.now().date() + timedelta(days=365)  # Asegurar que sea un objeto de fecha
            }
        )
        
        print(f"Ficha médica {'creada' if created else 'encontrada'}: {ficha_medica}")  # Depuración
            # Guardar el antecedente asociado al jugador en lugar de la ficha médica
        
        if form.is_valid():
            print("✅ Formulario válido.")
            antecedente = form.save(commit=False)
            antecedente.jugador = jugador
            antecedente.save()
            print(f"✅ Antecedente guardado correctamente: {antecedente}")
        else:
            print("❌ Error en el formulario:", form.errors)
            return self.form_invalid(form)
      

        return super().form_valid(form)

class VerAntecedenteView(DetailView):
    model = AntecedenteEnfermedades
    template_name = 'registro_medico/ver_antecedentes.html'
    context_object_name = 'antecedente'

    def get_object(self, queryset=None):
        jugador_id = self.kwargs.get('jugador_id')
        jugador = get_object_or_404(Jugador, id=jugador_id)
        print(f"Jugador encontrado: {jugador}")

        # Buscar la ficha médica asociada al jugador
        ficha_medica = RegistroMedico.objects.filter(jugador=jugador).first()
        print(f"Ficha médica encontrada: {ficha_medica}")

        # Obtener el antecedente basado en el jugador (en lugar de ficha médica)
        antecedente = get_object_or_404(AntecedenteEnfermedades, jugador=jugador)
        print(f"Antecedente encontrado: {antecedente}")

        return antecedente

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        antecedente = self.object  
        
        # Obtener la ficha médica asociada al jugador
        ficha_medica = RegistroMedico.objects.filter(jugador=antecedente.jugador).first()
        context['ficha_medica'] = ficha_medica

        # Pasar el perfil del usuario actual
        if hasattr(self.request.user, 'profile'):
            context['profile'] = self.request.user.profile

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
        profile = Profile.objects.get(user=self.request.user, rol='jugador')
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

    


# ✅ Cargar un estudio médico asociado a un JUGADOR (no ficha médica)
class CargarEstudioView(LoginRequiredMixin, CreateView):
    model = EstudiosMedico
    form_class = EstudioMedicoForm
    template_name = 'registro_medico/cargar_estudios.html'

    def form_valid(self, form):
        jugador = get_object_or_404(Jugador, id=self.kwargs['jugador_id'])
        print("🔍 Profile ID:", self.request.session.get("user_profile_id"))

        form.instance.jugador = jugador
        print("📦 Registro ID desde el POST:", self.request.POST.get('registro_id'))


        registro_id = self.request.POST.get('registro_id')
        if registro_id:
            form.instance.ficha_medica_id = registro_id
            print("✅ Estudio guardado:", form.instance)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jugador = get_object_or_404(Jugador, id=self.kwargs['jugador_id'])
        context['jugador'] = jugador

        registro_id = self.request.GET.get('registro_id')
        if registro_id:
            registro_medico = RegistroMedico.objects.filter(id=registro_id, jugador=jugador).first()
        else:
            registro_medico = RegistroMedico.objects.filter(jugador=jugador).order_by('-fecha_creacion').first()

        context['registro_medico'] = registro_medico
        return context

    def get_success_url(self):
        profile_id = self.request.session.get("user_profile_id")
        profile = Profile.objects.filter(id=profile_id).first()

        jugador_id = self.kwargs.get('jugador_id')
        registro_id = self.request.POST.get('registro_id')

        if profile:
            if profile.rol == 'jugador':
                return reverse_lazy('registroMedico:ver_estudios', kwargs={'jugador_id': jugador_id})
            elif profile.rol == 'medico' and registro_id:
                return reverse_lazy('registroMedico:registro_medico_update', kwargs={'registro_id': registro_id})

        return reverse_lazy('medico_home')  # Fallback en caso de problemas

# ✅ Listar estudios médicos filtrados por JUGADOR

class EstudiosMedicoListView(ListView):
    model = EstudiosMedico
    template_name = 'registro_medico/estudios_list.html'
    context_object_name = 'estudios'

    def get_queryset(self):
        jugador_id = self.kwargs.get('jugador_id')
        self.jugador_id = jugador_id  # guardamos para usar en el contexto
        return EstudiosMedico.objects.filter(jugador__id=jugador_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el registro médico actual para el jugador
        registro = RegistroMedico.objects.filter(jugador_id=self.jugador_id).order_by('-fecha_de_llenado').first()

        context['registro_estado'] = registro.estado if registro else 'SIN_REGISTRO'
        return context

# ✅ Eliminar un estudio médico
class EliminarEstudioView(DeleteView):
    model = EstudiosMedico
    template_name = 'registro_medico/eliminar_estudio_confirm.html'
    context_object_name = 'estudio'

    def get_success_url(self):
        jugador_id = self.object.jugador.id  # Obtiene el ID del jugador asociado
        return reverse_lazy('registroMedico:ver_estudios', kwargs={'jugador_id': jugador_id})

# ✅ Otra vista para eliminar un estudio médico (redirige a home del médico)
class EliminarEstudioMedicoView(DeleteView):
    model = EstudiosMedico
    template_name = 'registro_medico/eliminar_estudio_confirm.html'
    success_url = reverse_lazy('medico_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jugador'] = self.object.jugador  # Agrega el jugador al contexto
        return context