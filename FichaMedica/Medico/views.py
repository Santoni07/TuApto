from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import ListView
from django.db.models import Q
from django.db import transaction
from weasyprint import HTML
from persona.models import Jugador
from RegistroMedico.models import RegistroMedico, AntecedenteEnfermedades
from django.contrib.auth.mixins import LoginRequiredMixin
from Medico.models import Medico
from RegistroMedico.forms import *
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse

from django.urls import reverse


""" class MedicoHomeView(LoginRequiredMixin, ListView):
    model = Jugador
    template_name = 'medico/medico_home.html'
    context_object_name = 'jugadores'

            
            queryset = super().get_queryset().select_related('persona__profile').prefetch_related(
                Prefetch(
                    'jugadorcategoriaequipo_set',
                    queryset=JugadorCategoriaEquipo.objects.select_related(
                        'categoria_equipo__categoria__torneo', 'categoria_equipo__equipo'
                    )
                )
            )

            # Obtener el término de búsqueda
            search_query = self.request.GET.get('search_query', '').strip()

            # Verificar si el término de búsqueda es un DNI
            if search_query:
                if search_query.isdigit() and len(search_query) == 8:
                    # Filtrar según el DNI
                    queryset = queryset.filter(
                        Q(persona__profile__dni__icontains=search_query)
                    )
                elif search_query.isalpha():
                    # Búsqueda por nombre o apellido
                    queryset = queryset.filter(
                        Q(persona__profile__nombre__icontains=search_query) |
                        Q(persona__profile__apellido__icontains=search_query)
                    )
                else:
                    # Mostrar un mensaje de error si no cumple con el formato de DNI
                    messages.error(self.request, "El valor ingresado para la busqueda por DNI es incorrecto. Debe contener exactamente 8 números.")
                    return queryset.none()
            else:
                # Retornar un conjunto vacío si no se realiza ninguna búsqueda
                return queryset.none()

            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search_query', '')
        context['search_query'] = search_query

        try:
            context['medico'] = Medico.objects.get(profile=self.request.user.profile)
        except Medico.DoesNotExist:
            context['medico'] = None

        jugadores_info = []
        for jugador in context['jugadores']:
            jugador_info = {
                'id': jugador.id,
                'edad': jugador.persona.profile.edad,
                'dni': jugador.persona.profile.dni,
                'nombre': jugador.persona.profile.nombre,
                'apellido': jugador.persona.profile.apellido,
                'direccion': jugador.persona.direccion,
                'telefono': jugador.persona.telefono,
                'grupo_sanguineo': jugador.grupo_sanguineo,
                'cobertura_medica': jugador.cobertura_medica,
                'numero_afiliado': jugador.numero_afiliado,
                'categorias_equipo': [],
                'antecedentes': [],
                'estudios_medicos': [],
                'electro_basal_form': ElectroBasalForm(),
                'electro_esfuerzo_form': None,
                'cardiovascular_form': None,
                'laboratorio_form': None,
                'oftalmologico_form': None,
                'torax_form': None,
                'registro_medico_form': None,
                'estudio_medico_form': EstudioMedicoForm(),
                'ergonometria_cargado': False,  # Agregar la comprobación para el electrocardiograma
                'otros_examenes_form': OtrosExamenesClinicosForm(),
                
            }

            # Registro médico y antecedentes
            registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
            if registro_medico:
                jugador_info['registro_medico_estado'] = registro_medico.estado

                # Verificar si hay un electrocardiograma cargado
                estudios_medicos = EstudiosMedico.objects.filter(ficha_medica=registro_medico, tipo_estudio='ERGOMETRIA')
                jugador_info['ergonometria_cargado'] = estudios_medicos.exists()

                # Obtener estudios médicos
                estudios_medicos = EstudiosMedico.objects.filter(ficha_medica=registro_medico)
                jugador_info['estudios_medicos'] = [
                    {
                        'pk': estudio.pk,
                        'tipo': estudio.get_tipo_estudio_display(),
                        'archivo': estudio.archivo.url if estudio.archivo else None,
                        'observaciones': estudio.observaciones,
                    } for estudio in estudios_medicos
                ]

                jugador_info['registro_medico_estado'] = registro_medico.estado

                # Obtener antecedentes
                antecedentes = AntecedenteEnfermedades.objects.filter(idfichaMedica=registro_medico)
                jugador_info['antecedentes'] = [
                    {
                        'fue_operado': ant.fue_operado,
                        'toma_medicacion': ant.toma_medicacion,
                        'estuvo_internado': ant.estuvo_internado,
                        'sufre_hormigueos': ant.sufre_hormigueos,
                        'es_diabetico': ant.es_diabetico,
                        'es_asmatico': ant.es_amatico,
                        'es_alergico': ant.es_alergico,
                        'alerg_observ': ant.alerg_observ,
                        'antecedente_epilepsia': ant.antecedente_epilepsia,
                        'desviacion_columna': ant.desviacion_columna,
                        'dolor_cintura': ant.dolor_cintira,
                        'fracturas': ant.fracturas,
                        'dolores_articulares': ant.dolores_articulares,
                        'falta_aire': ant.falta_aire,
                        'traumatismos_craneo': ant.tramatismos_craneo,
                        'dolor_pecho': ant.dolor_pecho,
                        'perdida_conocimiento': ant.perdida_conocimiento,
                        'presion_arterial': ant.presion_arterial,
                        'muerte_subita_familiar': ant.muerte_subita_familiar,
                        'enfermedad_cardiaca_familiar': ant.enfermedad_cardiaca_familiar,
                        'soplo_cardiaco': ant.soplo_cardiaco,
                        'abstenerce_competencia': ant.abstenerce_competencia,
                        'antecedentes_coronarios_familiares': ant.antecedentes_coronarios_familiares,
                        'fumar_hipertension_diabetes': ant.fumar_hipertension_diabetes,
                        'consumo_cocaina_anabolicos': ant.consumo_cocaina_anabolicos,
                        'cca_observaciones': ant.cca_observaciones,
                    }
                    for ant in antecedentes
                ]
                
                # Instanciar formularios con datos existentes, si están presentes
                jugador_info['electro_basal_form'] = ElectroBasalForm(
                    instance=ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['electro_esfuerzo_form'] = ElectroEsfuerzoForm(
                    instance=ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['cardiovascular_form'] = CardiovascularForm(
                    instance=Cardiovascular.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['laboratorio_form'] = LaboratorioForm(
                    instance=Laboratorio.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['oftalmologico_form'] = OftalmologicoForm(
                    instance=Oftalmologico.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['torax_form'] = ToraxForm(
                    instance=Torax.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['otros_examenes_form'] = OtrosExamenesClinicosForm(
                    instance=OtrosExamenesClinicos.objects.filter(ficha_medica=registro_medico).first()
                )
            
            # Categorías y equipos asociados al jugador
            jugador_categoria_equipos = jugador.jugadorcategoriaequipo_set.all()
            jugador_info['categorias_equipo'] = [
                {
                    'nombre_categoria': jce.categoria_equipo.categoria.nombre,
                    'nombre_equipo': jce.categoria_equipo.equipo.nombre,
                    'torneo': jce.categoria_equipo.categoria.torneo.nombre
                } for jce in jugador_categoria_equipos
            ]
            
            jugadores_info.append(jugador_info)

        context['jugadores_info'] = jugadores_info
         # Pasar el pk al contexto
        context['pk'] = self.kwargs.get('pk') 
        return context

    def post(self, request, *args, **kwargs):
        print("Datos del formulario:", request.POST)
        #Comprobar si todos los formularios estan salvados 
        form_saved = False
        form_complete = False
        
        
        
        
        # Procesar el formulario de estudios médicos cuando el método sea POST
        form = EstudioMedicoForm(request.POST, request.FILES)
        if form.is_valid():
            estudio_medico = form.save(commit=False)
            # Asociar el estudio médico con el jugador o ficha médica correspondiente
            jugador_id = request.POST.get('jugador_id')  # O lo que uses para identificar al jugador
            jugador = Jugador.objects.get(id=jugador_id)
            print("Jugador ID:", jugador_id)
            registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
            print("Registro Médico:", registro_medico)
            if registro_medico:
                estudio_medico.ficha_medica = registro_medico
                estudio_medico.save()
                messages.success(request, "Estudio médico cargado exitosamente.")
            else:
                messages.error(request, "No se encontró el registro médico del jugador.")

            # Redirigir o mostrar el formulario actualizado
            return redirect('medico_home')  # Asegúrate de que esta URL esté definida en tus URLs
        else:
            print("Error : " ,form.errors)
            messages.error(request, "Hubo un error al cargar el estudio médico.")
            return redirect('medico_home')
         """
         

class MedicoHomeView(LoginRequiredMixin, ListView):
    model = Jugador
    template_name = 'medico/medico_home.html'
    context_object_name = 'jugadores'

    def get_queryset(self):
        # 🔹 Inicialmente, la lista está vacía
        queryset = Jugador.objects.all()

        # Obtener los valores de búsqueda desde la URL
        search_dni = self.request.GET.get('search_dni', '').strip()
        search_name = self.request.GET.get('search_name', '').strip()

        print("🔍 Búsqueda DNI:", search_dni)  # 🔹 Depuración: Ver si se recibe el DNI
        print("🔍 Búsqueda Nombre:", search_name)  # 🔹 Depuración: Ver si se recibe el nombre

        # Si no hay búsqueda, devolver una lista vacía
        if not search_dni and not search_name:
            print("🔹 No se ingresaron datos de búsqueda. Retornando lista vacía.")
            return Jugador.objects.none()

        # Filtrar por DNI
        if search_dni:
            if search_dni.isdigit() and len(search_dni) == 8:
                queryset = queryset.filter(persona__profile__dni__icontains=search_dni)
            else:
                messages.error(self.request, "El DNI ingresado debe contener exactamente 8 números.")
                return Jugador.objects.none()

        # 🔹 Filtrar por Nombre o Apellido (Búsqueda flexible)
        if search_name:
            palabras = search_name.strip().split()  # Dividir el texto en palabras
            consulta = Q()

            if len(palabras) == 1:
                # Si el usuario ingresa solo una palabra, buscar en nombre o apellido
                consulta = Q(persona__profile__nombre__icontains=palabras[0]) | Q(persona__profile__apellido__icontains=palabras[0])

            elif len(palabras) >= 2:
                # Si ingresa dos palabras, primero filtrar por la primera y luego por la segunda
                primer_termino = palabras[0]
                segundo_termino = palabras[1]

                # Buscar primero por nombre y luego por apellido, o viceversa
                consulta = (Q(persona__profile__nombre__icontains=primer_termino) & Q(persona__profile__apellido__icontains=segundo_termino)) | \
                        (Q(persona__profile__apellido__icontains=primer_termino) & Q(persona__profile__nombre__icontains=segundo_termino))

            queryset = queryset.filter(consulta)

        # 🔹 Depuración: Mostrar los jugadores encontrados
        jugadores_encontrados = queryset.values_list('id', 'persona__profile__nombre', 'persona__profile__apellido')
        
        if jugadores_encontrados:
            print("✅ Jugadores encontrados:")
            for jugador in jugadores_encontrados:
                print(f"   - ID: {jugador[0]}, Nombre: {jugador[1]}, Apellido: {jugador[2]}")
        else:
            print("⚠️ No se encontraron jugadores con los criterios de búsqueda.")

        return queryset
        

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pasar los valores actuales de búsqueda al contexto para mantenerlos en los inputs
        context['search_dni'] = self.request.GET.get('search_dni', '')
        context['search_name'] = self.request.GET.get('search_name', '')

        try:
            context['medico'] = Medico.objects.get(profile=self.request.user.profile)
        except Medico.DoesNotExist:
            context['medico'] = None

        jugadores_info = []
        for jugador in context['jugadores']:
            jugador_info = {
                'id': jugador.id,
                'edad': jugador.persona.profile.edad,
                'dni': jugador.persona.profile.dni,
                'nombre': jugador.persona.profile.nombre,
                'apellido': jugador.persona.profile.apellido,
                'direccion': jugador.persona.direccion,
                'telefono': jugador.persona.telefono,
                'grupo_sanguineo': jugador.grupo_sanguineo,
                'cobertura_medica': jugador.cobertura_medica,
                'numero_afiliado': jugador.numero_afiliado,
                'categorias_equipo': [],
                'antecedentes': [],
                'estudios_medicos': [],
                'electro_basal_form': ElectroBasalForm(),
                'electro_esfuerzo_form': ElectroEsfuerzoForm(),
                'cardiovascular_form': CardiovascularForm(),
                'laboratorio_form': LaboratorioForm(),
                'oftalmologico_form': OftalmologicoForm(),
                'torax_form': ToraxForm(),
                'registro_medico_form': RegistroMedicoForm(),
                'estudio_medico_form': EstudioMedicoForm(),
                'ergonometria_cargado': False,
                'electrocardiograma_cargado': False,  # Agregando la verificación del electrocardiograma
                'otros_examenes_form': OtrosExamenesClinicosForm(),
            }

            registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
            if registro_medico:
                jugador_info['registro_medico_estado'] = registro_medico.estado

                # Verificar si los estudios médicos han sido cargados
                jugador_info['ergonometria_cargado'] = EstudiosMedico.objects.filter(
                    ficha_medica=registro_medico, tipo_estudio='ERGOMETRIA'
                ).exists()

                jugador_info['electrocardiograma_cargado'] = EstudiosMedico.objects.filter(
                    ficha_medica=registro_medico, tipo_estudio='ELECTRO'
                ).exists()

                # Obtener todos los estudios médicos y mapearlos
                estudios_medicos = EstudiosMedico.objects.filter(ficha_medica=registro_medico)
                jugador_info['estudios_medicos'] = [
                    {
                        'pk': estudio.pk,
                        'tipo': estudio.get_tipo_estudio_display(),
                        'archivo': estudio.archivo.url if estudio.archivo else None,
                        'observaciones': estudio.observaciones,
                    } for estudio in estudios_medicos
                ]

                # Obtener antecedentes médicos del jugador
                antecedentes = AntecedenteEnfermedades.objects.filter(idfichaMedica=registro_medico)
                jugador_info['antecedentes'] = [
                    {
                        'fue_operado': ant.fue_operado,
                        'toma_medicacion': ant.toma_medicacion,
                        'estuvo_internado': ant.estuvo_internado,
                        'sufre_hormigueos': ant.sufre_hormigueos,
                        'es_diabetico': ant.es_diabetico,
                        'es_asmatico': ant.es_amatico,
                        'es_alergico': ant.es_alergico,
                        'alerg_observ': ant.alerg_observ,
                        'antecedente_epilepsia': ant.antecedente_epilepsia,
                        'desviacion_columna': ant.desviacion_columna,
                        'dolor_cintura': ant.dolor_cintira,
                        'fracturas': ant.fracturas,
                        'dolores_articulares': ant.dolores_articulares,
                        'falta_aire': ant.falta_aire,
                        'traumatismos_craneo': ant.tramatismos_craneo,
                        'dolor_pecho': ant.dolor_pecho,
                        'perdida_conocimiento': ant.perdida_conocimiento,
                        'presion_arterial': ant.presion_arterial,
                        'muerte_subita_familiar': ant.muerte_subita_familiar,
                        'enfermedad_cardiaca_familiar': ant.enfermedad_cardiaca_familiar,
                        'soplo_cardiaco': ant.soplo_cardiaco,
                        'abstenerce_competencia': ant.abstenerce_competencia,
                        'antecedentes_coronarios_familiares': ant.antecedentes_coronarios_familiares,
                        'fumar_hipertension_diabetes': ant.fumar_hipertension_diabetes,
                        'consumo_cocaina_anabolicos': ant.consumo_cocaina_anabolicos,
                        'cca_observaciones': ant.cca_observaciones,
                    }
                    for ant in antecedentes
                ]

                # Instanciar formularios con datos existentes
                jugador_info['electro_basal_form'] = ElectroBasalForm(
                    instance=ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['electro_esfuerzo_form'] = ElectroEsfuerzoForm(
                    instance=ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['cardiovascular_form'] = CardiovascularForm(
                    instance=Cardiovascular.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['laboratorio_form'] = LaboratorioForm(
                    instance=Laboratorio.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['oftalmologico_form'] = OftalmologicoForm(
                    instance=Oftalmologico.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['torax_form'] = ToraxForm(
                    instance=Torax.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['otros_examenes_form'] = OtrosExamenesClinicosForm(
                    instance=OtrosExamenesClinicos.objects.filter(ficha_medica=registro_medico).first()
                )

            # Obtener las categorías y equipos del jugador
            jugador_categoria_equipos = jugador.jugadorcategoriaequipo_set.all()
            jugador_info['categorias_equipo'] = [
                {
                    'nombre_categoria': jce.categoria_equipo.categoria.nombre,
                    'nombre_equipo': jce.categoria_equipo.equipo.nombre,
                    'torneo': jce.categoria_equipo.categoria.torneo.nombre
                } for jce in jugador_categoria_equipos
            ]

            jugadores_info.append(jugador_info)

        context['jugadores_info'] = jugadores_info
        context['pk'] = self.kwargs.get('pk')
        
        return context

    def post(self, request, *args, **kwargs):
        print("Datos del formulario:", request.POST)

        form_saved = False
        form_complete = False
        jugador_id = request.POST.get('jugador_id')

        form = EstudioMedicoForm(request.POST, request.FILES)
        if form.is_valid():
            estudio_medico = form.save(commit=False)

            jugador = get_object_or_404(Jugador, id=jugador_id)
            registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

            if registro_medico:
                estudio_medico.ficha_medica = registro_medico
                estudio_medico.save()
                messages.success(request, "✅ Estudio médico cargado exitosamente.")
                form_saved = True
            else:
                messages.error(request, "❌ No se encontró el registro médico del jugador.")
        else:
            print("Error:", form.errors)
            messages.error(request, "❌ Hubo un error al cargar el estudio médico.")

        # Asegurarse de que el queryset esté definido
        self.object_list = self.get_queryset()

        context = self.get_context_data()
        context['form_saved'] = form_saved
        context['jugador_id'] = jugador_id  # 🔑 Enviar el ID del jugador al contexto

        return render(request, 'medico/medico_home.html', context)
""" def electro_basal_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    
    if not registro_medico:
        return JsonResponse({"error": "No se encontró el registro médico del jugador."}, status=404)

    electro_basal = ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
    form_saved = False
    form_complete = False

    if request.method == 'POST':
        electro_basal_form = ElectroBasalForm(request.POST, instance=electro_basal)
        if electro_basal_form.is_valid():
            with transaction.atomic():
                electro_basal = electro_basal_form.save(commit=False)
                
                if not electro_basal.ficha_medica_id:
                    electro_basal.ficha_medica_id = registro_medico.idfichaMedica
                electro_basal.save()

                form_saved = True

            # Si es una solicitud AJAX, devolvemos JSON en lugar de renderizar un template
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        electro_basal_form = ElectroBasalForm(instance=electro_basal)
        if electro_basal:
            form_complete = all(
                getattr(electro_basal, field.name) 
                for field in electro_basal_form
            )

    # Renderizar solo para solicitudes normales (no AJAX)
    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'electro_basal_form': electro_basal_form,
        'form_saved': form_saved,
        'form_complete': form_complete,
    })
 """


def electro_basal_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    if not registro_medico:
        return JsonResponse({"error": "No se encontró el registro médico del jugador."}, status=404)


    electro_basal = ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
    form_saved = False
    form_complete = False
   
    if request.method == 'POST':
        electro_basal_form = ElectroBasalForm(request.POST, instance=electro_basal)
        if electro_basal_form.is_valid():
            with transaction.atomic():
                electro_basal = electro_basal_form.save(commit=False)

                # Asegurar que esté asociado con la ficha médica
                if not electro_basal.ficha_medica_id:
                    electro_basal.ficha_medica = registro_medico

                electro_basal.save()
                form_saved = True

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "✅ Formulario guardado exitosamente."})

    else:
        # 🔹 Inicializar el formulario con la instancia existente de ElectroBasal
        electro_basal_form = ElectroBasalForm(instance=electro_basal)

        # Verificar si el formulario está completo
        if electro_basal:
            electro_basal_form = ElectroBasalForm(instance=electro_basal)
            form_complete = all([
                getattr(electro_basal, field.name, None)
                for field in electro_basal_form.visible_fields()
            ])
        else:
            electro_basal_form = ElectroBasalForm()

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'electro_basal_form': electro_basal_form,
        'form_saved': form_saved,
        'form_complete': form_complete,
    })

def electro_esfuerzo_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    electro_esfuerzo = ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        electro_esfuerzo_form = ElectroEsfuerzoForm(request.POST, instance=electro_esfuerzo)
        if electro_esfuerzo_form.is_valid():
            with transaction.atomic():
                electro_esfuerzo = electro_esfuerzo_form.save(commit=False)
                electro_esfuerzo.ficha_medica = registro_medico
                electro_esfuerzo.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        electro_esfuerzo_form = ElectroEsfuerzoForm(instance=electro_esfuerzo)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'electro_esfuerzo_form': electro_esfuerzo_form,
    })

def otros_examenes_clinicos_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    otros_examenes = OtrosExamenesClinicos.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        otros_examenes_form = OtrosExamenesClinicosForm(request.POST, instance=otros_examenes)
        if otros_examenes_form.is_valid():
            with transaction.atomic():
                otros_examenes = otros_examenes_form.save(commit=False)
                otros_examenes.ficha_medica = registro_medico
                otros_examenes.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        otros_examenes_form = OtrosExamenesClinicosForm(instance=otros_examenes)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'otros_examenes_form': otros_examenes_form,
    })

def cardiovascular_view(request, jugador_id):
    # Obtener el jugador
    jugador = get_object_or_404(Jugador, id=jugador_id)

    # Obtener el registro médico del jugador
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    # Obtener los datos de cardiovascular del registro médico
    cardiovascular = Cardiovascular.objects.filter(ficha_medica=registro_medico).first()

    # Si se recibe el formulario POST
    if request.method == 'POST':
        cardiovascular_form = CardiovascularForm(request.POST, instance=cardiovascular)
        
        # Si el formulario es válido
        if cardiovascular_form.is_valid():
            with transaction.atomic():
                cardiovascular = cardiovascular_form.save(commit=False)
                cardiovascular.ficha_medica = registro_medico  # Asignar el registro médico
                cardiovascular.save()
            
            # Si es una petición AJAX, enviar una respuesta JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
        
        # Si no es AJAX, puedes mostrar los errores
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "errors": cardiovascular_form.errors})

    # Si es GET, o no se envió un POST
    else:
        cardiovascular_form = CardiovascularForm(instance=cardiovascular)

   
  
    
   
    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'cardiovascular_form': cardiovascular_form,
        
    })


def laboratorio_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    laboratorio = Laboratorio.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        laboratorio_form = LaboratorioForm(request.POST, instance=laboratorio)
        if laboratorio_form.is_valid():
            with transaction.atomic():
                laboratorio = laboratorio_form.save(commit=False)
                laboratorio.ficha_medica = registro_medico
                laboratorio.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        laboratorio_form = LaboratorioForm(instance=laboratorio)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'laboratorio_form': laboratorio_form,
    })


def torax_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    torax = Torax.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        torax_form = ToraxForm(request.POST, instance=torax)
        if torax_form.is_valid():
            with transaction.atomic():
                torax = torax_form.save(commit=False)
                torax.ficha_medica = registro_medico
                torax.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        torax_form = ToraxForm(instance=torax)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'torax_form': torax_form,
    })


def oftalmologico_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    oftalmologico = Oftalmologico.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        oftalmologico_form = OftalmologicoForm(request.POST, instance=oftalmologico)
        if oftalmologico_form.is_valid():
            with transaction.atomic():
                oftalmologico = oftalmologico_form.save(commit=False)
                oftalmologico.ficha_medica = registro_medico
                oftalmologico.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        oftalmologico_form = OftalmologicoForm(instance=oftalmologico)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'oftalmologico_form': oftalmologico_form,
    })




def registro_medico_update_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    if request.method == 'POST':
        print(request.POST)  # Verifica los valores enviados en el formulario
        registro_medico_form = RegistroMedicoUpdateForm(request.POST, instance=registro_medico)
        if registro_medico_form.is_valid():
            with transaction.atomic():
                registro_medico = registro_medico_form.save(commit=False)
                
                # Obtener al médico logueado
                medico = Medico.objects.filter(profile=request.user.profile).first()
                if medico:
                    registro_medico.medico = medico  # Asignar el médico logueado

                registro_medico.save()
                return redirect('registro_medico_update_view', jugador_id=jugador_id)
        else:
            # Si el formulario no es válido, se puede imprimir para depurar
            print("Formulario no válido:", registro_medico_form.errors)
    else:
        registro_medico_form = RegistroMedicoUpdateForm(instance=registro_medico)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'registro_medico': registro_medico,  # Pasar el registro médico al contexto
        'registro_medico_form': registro_medico_form,
    })


def ficha_medica_views(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

        # Verificar si el usuario tiene un perfil de médico asociado
    try:
        medico = Medico.objects.get(profile=request.user.profile)
        rol_usuario = medico.profile.rol
    except Medico.DoesNotExist:
        rol_usuario = None  # En caso de que no sea un médico

    print("Rol del usuario logueado:", rol_usuario)
    
    
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    if request.method == 'POST':
        registro_medico_form = RegistroMedicoUpdateForm(request.POST, instance=registro_medico)
        if registro_medico_form.is_valid():
            registro_medico = registro_medico_form.save(commit=False)
            medico = Medico.objects.filter(profile=request.user.profile).first()
            if medico:
                registro_medico.medico = medico
            registro_medico.save()
            return redirect('ficha_medica', jugador_id=jugador_id)
    else:
        registro_medico_form = RegistroMedicoUpdateForm(instance=registro_medico)

    antecedentes = AntecedenteEnfermedades.objects.filter(idfichaMedica=registro_medico)
    electro_basal = ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
    electro_esfuerzo = ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()
    cardiovascular = Cardiovascular.objects.filter(ficha_medica=registro_medico).first()
    laboratorio = Laboratorio.objects.filter(ficha_medica=registro_medico).first()
    oftalmologico = Oftalmologico.objects.filter(ficha_medica=registro_medico).first()
    torax = Torax.objects.filter(ficha_medica=registro_medico).first()
    otros_examenes = OtrosExamenesClinicos.objects.filter(ficha_medica=registro_medico).first()

    # Convertir URLs relativas de imágenes en absolutas
    for categoria in jugador.jugadorcategoriaequipo_set.all():
        if categoria.categoria_equipo.categoria.torneo.imagen:
             categoria.categoria_equipo.categoria.torneo.imagen_url = request.build_absolute_uri(
                categoria.categoria_equipo.categoria.torneo.imagen.url
            )
    
    if registro_medico.medico and registro_medico.medico.firma:
        registro_medico.medico.firma = request.build_absolute_uri(registro_medico.medico.firma.url)

    jugador_info = {
        'id': jugador.id,
        'edad': jugador.persona.profile.edad,
        'dni': jugador.persona.profile.dni,
        'nombre': jugador.persona.profile.nombre,
        'rol_usuario': jugador.persona.profile.rol,
        'apellido': jugador.persona.profile.apellido,
        'direccion': jugador.persona.direccion,
        'telefono': jugador.persona.telefono,
        'grupo_sanguineo': jugador.grupo_sanguineo,
        'cobertura_medica': jugador.cobertura_medica,
        'numero_afiliado': jugador.numero_afiliado,
        'categorias_equipo': [
            {
                'nombre_categoria': jce.categoria_equipo.categoria.nombre,
                'nombre_equipo': jce.categoria_equipo.equipo.nombre,
                'torneo': jce.categoria_equipo.categoria.torneo.nombre,
                 'imagen': jce.categoria_equipo.categoria.torneo.imagen.url if jce.categoria_equipo.categoria.torneo.imagen else None,
                'descripcion': jce.categoria_equipo.categoria.torneo.descripcion,
                'direccion': jce.categoria_equipo.categoria.torneo.direccion,
                'telefono': jce.categoria_equipo.categoria.torneo.telefono,
            }
            for jce in jugador.jugadorcategoriaequipo_set.all()
        ],
        'antecedentes': [{'fue_operado': ant.fue_operado,
                            'toma_medicacion': ant.toma_medicacion,
                            'estuvo_internado': ant.estuvo_internado,
                            'sufre_hormigueos': ant.sufre_hormigueos,
                            'es_diabetico': ant.es_diabetico,
                            'es_asmatico': ant.es_amatico,
                            'es_alergico': ant.es_alergico,
                            'alerg_observ': ant.alerg_observ,
                            'antecedente_epilepsia': ant.antecedente_epilepsia,
                            'desviacion_columna': ant.desviacion_columna,
                            'dolor_cintura': ant.dolor_cintira,
                            'fracturas': ant.fracturas,
                            'dolores_articulares': ant.dolores_articulares,
                            'falta_aire': ant.falta_aire,
                            'traumatismos_craneo': ant.tramatismos_craneo,
                            'dolor_pecho': ant.dolor_pecho,
                            'perdida_conocimiento': ant.perdida_conocimiento,
                            'presion_arterial': ant.presion_arterial,
                            'muerte_subita_familiar': ant.muerte_subita_familiar,
                            'enfermedad_cardiaca_familiar': ant.enfermedad_cardiaca_familiar,
                            'soplo_cardiaco': ant.soplo_cardiaco,
                            'abstenerce_competencia': ant.abstenerce_competencia,
                            'antecedentes_coronarios_familiares': ant.antecedentes_coronarios_familiares,
                            'fumar_hipertension_diabetes': ant.fumar_hipertension_diabetes,
                            'consumo_cocaina_anabolicos': ant.consumo_cocaina_anabolicos,
                            'cca_observaciones': ant.cca_observaciones,} for ant in antecedentes],
        'electro_basal_form': ElectroBasalForm(instance=electro_basal),
        'electro_esfuerzo_form': ElectroEsfuerzoForm(instance=electro_esfuerzo),
        'cardiovascular_form': CardiovascularForm(instance=cardiovascular),
        'laboratorio_form': LaboratorioForm(instance=laboratorio),
        'oftalmologico_form': OftalmologicoForm(instance=oftalmologico),
        'torax_form': ToraxForm(instance=torax),
        'otros_examenes_form': OtrosExamenesClinicosForm(instance=otros_examenes),
        
        'registro_medico_form': registro_medico_form,
    }

    # Generar y descargar PDF si se solicita
    if request.GET.get('descargar_pdf') == 'true':
        html_content = render_to_string('medico/medico_views.html', {
            'jugador_info': jugador_info,
            'registro_medico': registro_medico,
        })

        # Extraer solo el contenido del bloque de HTML
        start_tag = '<section id="content">'
        end_tag = '</section>'
        content_start = html_content.find(start_tag)
        content_end = html_content.find(end_tag) + len(end_tag)
        content_to_pdf = html_content[content_start:content_end]

        html_string = f"""
                            <!DOCTYPE html>
                            <html lang="es">
                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Ficha Médica</title>
                                <style>
                                    body {{
                                        font-family: 'Arial', sans-serif;
                                        font-size: 8px;
                                        color: #333;
                                        margin: 0px 0px 0px 0px;
                                        padding: 0px 0px 0px 0px;
                                    }}
                                    /* Estilos del header */
                                    header {{
                                        display: flex;
                                        align-items: center; /* Alinea verticalmente el contenido */
                                    }}
                                  
                                    /* Estilo para el contenedor del logo */
                                    header .logo {{
                                        display: flex;
                                        align-items: center; /* Alinea verticalmente el logo y el texto */
                                        margin-right: auto; /* Empuja el logo hacia la izquierda */
                                    }}

                                    /* Estilo para la imagen del logo */
                                    header .logo img {{
                                        width: 80px; /* Controla el tamaño del logo */
                                    }}

                                    /* Estilo para el título del sitio */
                                    header .sitename {{
                                        margin-left: 10px; /* Espacio entre el logo y el texto */
                                        font-weight: bold; /* Hace el texto en negrita */
                                        color: black; /* Pone el texto en negro */
                                        text-decoration: none; /* Elimina cualquier subrayado */
                                    }}
                                      /* Estilo para el enlace (elimina subrayado) */
                                    header .logo a {{
                                        text-decoration: none; /* Elimina el subrayado en el enlace */
                                    }}

                                    /* Contenedor principal */
                                    .container {{
                                        
                                       
                                        
                                    }}

                                    /* Tipografía */
                                    h1, h2, h3, h4 {{
                                        color: {{ header_color|default:"#0056b3" }};
                                        text-align: center;
                                         margin: 0px 0px 0px 0px;
                                        padding: 0px 0px 0px 0px;
                                        font-weight: bold;
                                        font-size: 10px;
                                    }}

                                    p {{
                                        margin: 0;
                                        line-height: 1.5;
                                    }}

                                    /* Tarjetas */
                                    .card {{
                                        border: 1px solid #ddd;
                                        border-radius: 4px;
                                        margin-bottom: 5px;
                                        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
                                    }}

                                    .card-header {{
                                        background-color: {{ card_header_bg|default:"#f7f7f7" }};
                                        border-bottom: 1px solid #ddd;
                                        text-align: center;
                                        font-size: 12px;
                                        font-weight: bold;
                                  
                                        
                                    }}

                                      .card-body {{
                                        
                                        line-height: 1.4;
                                        font-size: 10px;
                                       
                                        
                                    }}

                                    /* Filas y columnas */
                                    .row {{
                                        display: flex;
                                        flex-wrap: wrap;
                                        margin: 0 -8px;
                                    }}

                                    .col-md-6 {{
                                        flex: 0 0 50%;
                                        max-width: 50%;
                                     
                                        
                                    }}

                                    .col-md-4 {{
                                        flex: 0 0 33.3333%;
                                        max-width: 33.3333%;
                                        
                                    }}

                                    .col-md-9 {{
                                        flex: 0 0 75%;
                                        ali
                                        max-width: 75%;
                                       
                                        text-align: justify;
                                    }}

                                    .col-md-3 {{
                                        flex: 0 0 25%;
                                        max-width: 25%;
                                      
                                        
                                    }}

                                    /* Imágenes */
                                    img {{
                                        max-width: 80px;
                                        height: auto;
                                        display: block;
                                        margin: 0 auto;
                                    }}
                                    .logo_header{{
                                        max-width: 80px;
                                        height: auto;
                                        display: block;
                                        margin: 0 auto; 
                                    }}
                                    /* Tablas */
                                    table {{
                                      
                                        border-collapse: collapse;
                                   
                                        
                                    }}

                                    table th, table td {{
                                        border: 1px solid #ddd;
                                        
                                        text-align: left;
                                        font-size: 10px;
                                    }}

                                    table th {{
                                        background-color: {{ table_header_bg|default:"#f1f1f1" }};
                                        font-weight: bold;
                                        padding: 0px;
                                    }}

                                    /* Botones */
                                    .btn {{
                                        display: inline-block;
                                        font-size: 10px;
                                        font-weight: bold;
                                        text-align: center;
                                        color: white;
                                        background-color: {{ btn_bg_color|default:"#007bff" }};
                                        border: none;
                                        padding: 3px 8px;
                                        border-radius: 4px;
                                        text-decoration: none;
                                    }}

                                    .btn:hover {{
                                        background-color: {{ btn_hover_bg|default:"#0056b3" }};
                                    }}
                                        .row {{
                                            display: flex;
                                            justify-content: center; /* Centra horizontalmente */
                                            align-items: center; /* Centra verticalmente */
                                             margin: 0px 0px 0px 0px;
                                        padding: 0px 0px 0px 0px;
                                        }}

                                        .col-md-6 {{
                                            text-align: center; /* Asegura que el contenido interno esté centrado */
                                        }}

                                        /* Opcional: Estilo para la imagen de la firma */
                                        .img-fluid {{
                                            display: block;
                                            margin: 0 auto; /* Centra la imagen horizontalmente */
                                            max-width: 150px;
                                            height: auto;
                                        }}

                                        /* Opcional: Estilo para el texto */
                                        p {{
                                            margin: 0.5rem 0;
                                        }}
                                </style>
                            </head>
                            <body>
                                {content_to_pdf}
                            </body>
                            </html>
                        """
        

        # Crear PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ficha_medica_{jugador_info['apellido']}_{jugador_info['nombre']}.pdf"'
        return response

    context = {
        'jugador_info': jugador_info,
        'registro_medico': registro_medico,
        'rol_usuario': rol_usuario,
    }
    return render(request, 'medico/medico_views.html', context)

def eliminar_ficha_medica(request, jugador_id):
    print("🔹 Iniciando eliminación de ficha médica...")

    # Obtener la ficha médica del jugador
    registro_medico = RegistroMedico.objects.filter(jugador__id=jugador_id).first()
    if not registro_medico:
        print("⚠️ No se encontró la ficha médica del jugador.")
        messages.error(request, "No se encontró la ficha médica del jugador.")
        return redirect('medico_home')

    print("✅ Ficha médica encontrada:", registro_medico)

    # Obtener el perfil del médico
    medico = Medico.objects.filter(profile=request.user.profile).first()
    if not medico:
        print("⚠️ No se encontró el perfil del médico asociado.")
        messages.error(request, "No se encontró el perfil del médico asociado.")
        return redirect('medico_home')

    rol_usuario = medico.profile.rol
    print(f"✅ Médico identificado: {medico}")
    print(f"🔍 Valor exacto de rol_usuario: {repr(rol_usuario)}")

    # Verificar permisos
    if rol_usuario.strip().lower() in ['médico', 'medico', 'administrador']:
        print("✅ Permiso concedido. Registrando eliminación...")

        # Guardar el registro en el modelo de EliminacionFichaMedica
        EliminacionFichaMedica.objects.create(
            jugador=f"{registro_medico.jugador.persona.profile.apellido} {registro_medico.jugador.persona.profile.nombre}",
            medico=f"{medico.profile.apellido} {medico.profile.nombre}",
            fecha_eliminacion=now()
        )

        # Eliminar la ficha médica
        registro_medico.delete()
        messages.success(request, "La ficha médica ha sido eliminada correctamente y registrada en el historial.")
        print("✅ Ficha médica eliminada con éxito y registrada.")
        return redirect('medico_home')
    else:
        print("⛔ No tienes permisos para eliminar esta ficha médica.")
        messages.error(request, "No tienes permisos para eliminar esta ficha médica.")
        return redirect('medico_home')