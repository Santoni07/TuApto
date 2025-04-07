from django.contrib import messages
from django.http import HttpResponse
from weasyprint import HTML
from django.utils.html import format_html
from django.http import HttpResponse
from django.views.generic import ListView,UpdateView
from django.db.models import Q
from django.db import transaction
from weasyprint import HTML
from django.views.generic import View
from account.models import Profile
from persona.models import Jugador,JugadorCategoriaEquipo
from RegistroMedico.models import RegistroMedico, AntecedenteEnfermedades
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from Cus.models import Cus
from RegistroMedico.forms import *
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import reverse
from estudiante.models import Estudiante, AntecedentesCUS
from estudiante.models import Tutor
from account.models import Profile
from Medico.models import Medico
from Cus.models import *
from Cus.form import *
#Vista medico_home
class MedicoHomeView(LoginRequiredMixin, ListView):
    model = Jugador
    template_name = 'medico/medico_home.html'
    context_object_name = 'jugadores'

    def get_queryset(self):
        queryset = Jugador.objects.all()
        search_dni = self.request.GET.get('search_dni', '').strip()
        search_name = self.request.GET.get('search_name', '').strip()

        if not search_dni and not search_name:
            return Jugador.objects.none()

        if search_dni:
            if search_dni.isdigit() and len(search_dni) == 8:
                queryset = queryset.filter(persona__profile__dni__icontains=search_dni)
            else:
                messages.error(self.request, "El DNI ingresado debe contener exactamente 8 números.")
                return Jugador.objects.none()

        if search_name:
            palabras = search_name.strip().split()
            consulta = Q()

            if len(palabras) == 1:
                consulta = Q(persona__profile__nombre__icontains=palabras[0]) | Q(persona__profile__apellido__icontains=palabras[0])
            elif len(palabras) >= 2:
                primer_termino = palabras[0]
                segundo_termino = palabras[1]
                consulta = (Q(persona__profile__nombre__icontains=primer_termino) & Q(persona__profile__apellido__icontains=segundo_termino)) | \
                        (Q(persona__profile__apellido__icontains=primer_termino) & Q(persona__profile__nombre__icontains=segundo_termino))

            queryset = queryset.filter(consulta)

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_dni'] = self.request.GET.get('search_dni', '')
        context['search_name'] = self.request.GET.get('search_name', '')

        profile_id = self.request.session.get("user_profile_id")
        print(f"🔍 Profile ID: {profile_id}")
        profile = Profile.objects.filter(id=profile_id).first()
        context['profile'] = profile
        print(f"🔍 Profile ID: {profile_id}")
        

        if profile:
            context['medico'] = Medico.objects.filter(profile=profile).first()
            print(f"🔍 Medico asociado al perfil: {context['medico']}")
        else:
            context['medico'] = None

        jugadores_info = []
        registro_seleccionado = self.request.GET.get('registro_id', None)  # 🔹 Obtiene el registro seleccionado

        if 'jugadores' in context and context['jugadores'].exists():
            for jugador in context['jugadores']:
                registros_medicos = RegistroMedico.objects.filter(jugador=jugador)  # 🔹 Obtener TODOS los registros médicos

                for registro in registros_medicos:  # 🔹 Asegurarse de recorrer TODOS los registros
                    jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(
                        jugador=jugador,
                        categoria_equipo__categoria__torneo=registro.torneo  # 🔹 Asociar con el torneo correcto
                    ).first()

                    jugador_info = {
                        'id': jugador.id,
                        'dni': jugador.persona.profile.dni,
                        'nombre': jugador.persona.profile.nombre,
                        'apellido': jugador.persona.profile.apellido,
                        'categoria': jugador_categoria_equipo.categoria_equipo.categoria.nombre if jugador_categoria_equipo else "Sin categoría",
                        'equipo': jugador_categoria_equipo.categoria_equipo.equipo.nombre if jugador_categoria_equipo else "Sin equipo",
                        'torneo': registro.torneo.nombre if registro.torneo else "Sin torneo",  # 🔹 Mostrar el torneo del registro
                        'estado': registro.estado,  # 🔹 Mostrar el estado del registro
                        'registro_id': registro.id,  # 🔹 ID único por registro
                        
                    }

                
                    jugadores_info.append(jugador_info)  # 🔹 AGREGAR CADA REGISTRO MÉDICO A LA LISTA

        context['jugadores_info'] = jugadores_info  # 🔹 Ahora se mostrarán todos los registros médicos en filas separadas
        return context

    def post(self, request, *args, **kwargs):
            print("📌 Datos del formulario:", request.POST)

            form_saved = False
            form_complete = False
            jugador_id = request.POST.get('jugador_id')
            registro_id = request.POST.get('registro_id')  # Asegurar que el ID del registro se pasa correctamente

            form = EstudioMedicoForm(request.POST, request.FILES)
            if form.is_valid():
                estudio_medico = form.save(commit=False)

                # Obtener el registro médico específico
                jugador = get_object_or_404(Jugador, id=jugador_id)
                registro_medico = get_object_or_404(RegistroMedico, id=registro_id, jugador=jugador)

                if registro_medico:
                    estudio_medico.ficha_medica = registro_medico
                    estudio_medico.save()
                    messages.success(request, "✅ Estudio médico cargado exitosamente.")
                    form_saved = True
                else:
                    messages.error(request, "❌ No se encontró el registro médico del jugador.")
            else:
                print("❌ Error en el formulario:", form.errors)
                messages.error(request, "❌ Hubo un error al cargar el estudio médico.")

            # Asegurarse de que el queryset esté definido
            self.object_list = self.get_queryset()

            context = self.get_context_data()
            context['form_saved'] = form_saved
            context['jugador_id'] = jugador_id  # 🔑 Enviar el ID del jugador al contexto
            context['registro_id'] = registro_id  # 🔑 Enviar el ID del registro médico al contexto

            return render(request, 'medico/medico_home.html', context)


#Manejo de los formularios
def manejar_formulario_medico(request, jugador_id, registro_id, modelo, formulario_clase, template_name='medico/medico_home.html'):

    print(f"🛠 Debug - jugador_id: {jugador_id}, registro_id: {registro_id} (Tipo: {type(registro_id)})")
    
    # Validar que registro_id sea un número entero
    try:
        registro_id = int(registro_id)
    except ValueError:
        return HttpResponse("Error: registro_id debe ser un número entero.", status=400)

    # Obtener jugador y registro médico
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = get_object_or_404(RegistroMedico, id=registro_id, jugador=jugador)

    print(f"✅ Registro Médico encontrado: {registro_medico}")

    # Buscar la instancia del modelo relacionado con la ficha médica
    instancia = modelo.objects.filter(ficha_medica=registro_medico).first()

    if request.method == 'POST':
        formulario = formulario_clase(request.POST, instance=instancia)
        if formulario.is_valid():
            with transaction.atomic():
                instancia = formulario.save(commit=False)
                instancia.ficha_medica = registro_medico
                instancia.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        formulario = formulario_clase(instance=instancia)

    return render(request, template_name, {
        'jugador': jugador,
        f'{modelo.__name__.lower()}_form': formulario,
    })


# Vistas utilizando la función genérica
def electro_basal_view(request, jugador_id, registro_id):
   return manejar_formulario_medico(request, jugador_id, registro_id, ElectroBasal, ElectroBasalForm)

def electro_esfuerzo_view(request, jugador_id, registro_id):
    return manejar_formulario_medico(request, jugador_id, registro_id, ElectroEsfuerzo, ElectroEsfuerzoForm)

def otros_examenes_clinicos_view(request, jugador_id, registro_id):
    return manejar_formulario_medico(request, jugador_id, registro_id, OtrosExamenesClinicos, OtrosExamenesClinicosForm)

def cardiovascular_view(request, jugador_id, registro_id):
    return manejar_formulario_medico(request, jugador_id, registro_id, Cardiovascular, CardiovascularForm)

def laboratorio_view(request, jugador_id, registro_id):
    return manejar_formulario_medico(request, jugador_id, registro_id, Laboratorio, LaboratorioForm)

def torax_view(request, jugador_id, registro_id):
    return manejar_formulario_medico(request, jugador_id, registro_id, Torax, ToraxForm)

def oftalmologico_view(request, jugador_id, registro_id):
    return manejar_formulario_medico(request, jugador_id, registro_id, Oftalmologico, OftalmologicoForm)



@login_required
def registro_medico_update_view(request, registro_id):
    registro_medico = get_object_or_404(RegistroMedico, id=registro_id)
    jugador = registro_medico.jugador

    if request.method == 'POST':
        print(request.POST)

        estado_anterior = registro_medico.estado
        registro_medico_form = RegistroMedicoUpdateForm(request.POST, instance=registro_medico)
        estudio_medico_form = EstudioMedicoForm(request.POST, request.FILES)

        # CARGA DE ESTUDIO
        if 'cargar_estudio' in request.POST and estudio_medico_form.is_valid():
            estudio = estudio_medico_form.save(commit=False)
            estudio.jugador = jugador
            estudio.ficha_medica = registro_medico
            estudio.save()
            print(f"✅ Estudio guardado: {estudio.tipo_estudio} - ID: {estudio.idestudio}")
            messages.success(request, "✅ Estudio médico cargado exitosamente.")
            return redirect('registro_medico_update', registro_id=registro_medico.id)

        # GUARDAR SOLO REGISTRO
        elif 'guardar_registro' in request.POST and registro_medico_form.is_valid():
            with transaction.atomic():
                registro_medico = registro_medico_form.save(commit=False)
                if not registro_medico.estado:
                    registro_medico.estado = estado_anterior

                profile_id = request.session.get("user_profile_id")
                profile = Profile.objects.filter(id=profile_id).first()
                if profile:
                    medico = Medico.objects.filter(profile=profile).first()
                    if medico:
                        registro_medico.medico = medico

                registro_medico.save()
                messages.success(request, "✅ Ficha médica actualizada.")
                return redirect('medico_home')

        # GUARDAR FICHA COMPLETA
        elif 'guardar_ficha_completa' in request.POST:
            with transaction.atomic():
                # Guardar Registro Médico
                if registro_medico_form.is_valid():
                    registro_medico = registro_medico_form.save(commit=False)
                    registro_medico.estado = "APROBADA"
                    profile_id = request.session.get("user_profile_id")
                    profile = Profile.objects.filter(id=profile_id).first()
                    if profile:
                        medico = Medico.objects.filter(profile=profile).first()
                        if medico:
                            registro_medico.medico = medico
                    registro_medico.save()

                # Guardar formularios médicos
                forms_valid = True

                electro_basal_form = ElectroBasalForm(request.POST, instance=ElectroBasal.objects.filter(ficha_medica=registro_medico).first() or ElectroBasal(ficha_medica=registro_medico))
                if electro_basal_form.is_valid(): electro_basal_form.save()
                else: 
                    print("❌ Error en ElectroBasalForm:", electro_basal_form.errors)
                    forms_valid = False

                electro_esfuerzo_form = ElectroEsfuerzoForm(request.POST, instance=ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first() or ElectroEsfuerzo(ficha_medica=registro_medico))
                if electro_esfuerzo_form.is_valid(): electro_esfuerzo_form.save()
                else:
                    print("❌ Error en ElectroEsfuerzoForm:", electro_esfuerzo_form.errors)
                    forms_valid = False

                cardiovascular_form = CardiovascularForm(request.POST, instance=Cardiovascular.objects.filter(ficha_medica=registro_medico).first() or Cardiovascular(ficha_medica=registro_medico))
                if cardiovascular_form.is_valid(): cardiovascular_form.save()
                else: 
                    print("❌ Error en CardiovascularForm:", cardiovascular_form.errors)
                    forms_valid = False

                laboratorio_form = LaboratorioForm(request.POST, instance=Laboratorio.objects.filter(ficha_medica=registro_medico).first() or Laboratorio(ficha_medica=registro_medico))
                if laboratorio_form.is_valid(): laboratorio_form.save()
                else: 
                    print("❌ Error en LaboratorioForm:", laboratorio_form.errors)
                    forms_valid = False

                oftalmologico_form = OftalmologicoForm(request.POST, instance=Oftalmologico.objects.filter(ficha_medica=registro_medico).first() or Oftalmologico(ficha_medica=registro_medico))
                if oftalmologico_form.is_valid(): oftalmologico_form.save()
                else:
                    print("❌ Error en OftalmologicoForm:", oftalmologico_form.errors)
                    forms_valid = False

                torax_form = ToraxForm(request.POST, instance=Torax.objects.filter(ficha_medica=registro_medico).first() or Torax(ficha_medica=registro_medico))
                if torax_form.is_valid(): torax_form.save()
                else:
                    print("❌ Error en ToraxForm:", torax_form.errors)
                    forms_valid = False

                otros_examenes_form = OtrosExamenesClinicosForm(request.POST, instance=OtrosExamenesClinicos.objects.filter(ficha_medica=registro_medico).first() or OtrosExamenesClinicos(ficha_medica=registro_medico))
                if otros_examenes_form.is_valid(): otros_examenes_form.save()
                else:
                    print("❌ Error en OtrosExamenesClinicosForm:", otros_examenes_form.errors)
                    forms_valid = False

                if forms_valid:
                    messages.success(request, "✅ Ficha médica completada y aprobada correctamente.")
                else:
                    messages.warning(request, "⚠️ Algunos formularios no se pudieron guardar. Por favor revisá.")

                return redirect('medico_home')

        else:
            print("🛑 Errores en RegistroMedicoForm:")
            print(registro_medico_form.errors)

            print("🛑 Errores en EstudioMedicoForm:")
            print(estudio_medico_form.errors)
            messages.error(request, "❌ Error al procesar el formulario.")

    else:
        registro_medico_form = RegistroMedicoUpdateForm(instance=registro_medico)
        estudio_medico_form = EstudioMedicoForm()

    jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(
        jugador=jugador,
        categoria_equipo__categoria__torneo=registro_medico.torneo
    ).first()

    context = {
        'jugador': jugador,
        'registro_medico': registro_medico,
        'registro_medico_form': registro_medico_form,
        'estudio_medico_form': estudio_medico_form,
        'nombre': jugador.persona.profile.nombre,
        'apellido': jugador.persona.profile.apellido,
        'edad': jugador.persona.profile.edad,
        'dni': jugador.persona.profile.dni,
        'direccion': jugador.persona.direccion,
        'telefono': jugador.persona.telefono,
        'grupo_sanguineo': jugador.grupo_sanguineo,
        'cobertura_medica': jugador.cobertura_medica,
        'numero_afiliado': jugador.numero_afiliado,
        'torneo_descripcion': registro_medico.torneo.descripcion if registro_medico.torneo else "Sin Descripción",
        'torneo_direccion': registro_medico.torneo.direccion if registro_medico.torneo else "Sin Dirección",
        'torneo_telefono': registro_medico.torneo.telefono if registro_medico.torneo else "Sin Teléfono",
        'imagen_torneo': registro_medico.torneo.imagen.url if registro_medico.torneo and registro_medico.torneo.imagen else None,
        'categoria': jugador_categoria_equipo.categoria_equipo.categoria.nombre if jugador_categoria_equipo else "Sin categoría",
        'equipo': jugador_categoria_equipo.categoria_equipo.equipo.nombre if jugador_categoria_equipo else "Sin equipo",
        'electrocardiograma_cargado': EstudiosMedico.objects.filter(jugador=jugador, tipo_estudio='ELECTRO').exists(),
        'ergonometria_cargado': EstudiosMedico.objects.filter(jugador=jugador, tipo_estudio='ERGOMETRIA').exists(),
        'antecedentes': [
            {
                'fue_operado': ant.fue_operado,
                'toma_medicacion': ant.toma_medicacion,
                'estuvo_internado': ant.estuvo_internado,
                'sufre_hormigueos': ant.sufre_hormigueos,
                'es_diabetico': ant.es_diabetico,
                'es_asmatico': ant.es_asmatico,
                'es_alergico': ant.es_alergico,
                'alerg_observ': ant.alerg_observ,
                'antecedente_epilepsia': ant.antecedente_epilepsia,
                'desviacion_columna': ant.desviacion_columna,
                'dolor_cintura': ant.dolor_cintura,
                'fracturas': ant.fracturas,
                'dolores_articulares': ant.dolores_articulares,
                'falta_aire': ant.falta_aire,
                'traumatismos_craneo': ant.traumatismos_craneo,
                'dolor_pecho': ant.dolor_pecho,
                'perdida_conocimiento': ant.perdida_conocimiento,
                'presion_arterial': ant.presion_arterial,
                'muerte_subita_familiar': ant.muerte_subita_familiar,
                'enfermedad_cardiaca_familiar': ant.enfermedad_cardiaca_familiar,
                'soplo_cardiaco': ant.soplo_cardiaco,
                'abstenerce_competencia': ant.abstenerse_competencia,
                'antecedentes_coronarios_familiares': ant.antecedentes_coronarios_familiares,
                'fumar_hipertension_diabetes': ant.fumar_hipertension_diabetes,
                'consumo_cocaina_anabolicos': ant.consumo_cocaina_anabolicos,
                'cca_observaciones': ant.cca_observaciones,
            }
            for ant in AntecedenteEnfermedades.objects.filter(jugador=jugador)
        ],
        'estudios_medicos': [
            {
                'pk': estudio.pk,
                'tipo': estudio.get_tipo_estudio_display(),
                'archivo': estudio.archivo.url if estudio.archivo else None,
                'observaciones': estudio.observaciones,
            }
            for estudio in EstudiosMedico.objects.filter(jugador=jugador)
        ],
        'electro_basal_form': ElectroBasalForm(instance=ElectroBasal.objects.filter(ficha_medica=registro_medico).first() or ElectroBasal(ficha_medica=registro_medico)),
        'electro_esfuerzo_form': ElectroEsfuerzoForm(instance=ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first() or ElectroEsfuerzo(ficha_medica=registro_medico)),
        'cardiovascular_form': CardiovascularForm(instance=Cardiovascular.objects.filter(ficha_medica=registro_medico).first() or Cardiovascular(ficha_medica=registro_medico)),
        'laboratorio_form': LaboratorioForm(instance=Laboratorio.objects.filter(ficha_medica=registro_medico).first() or Laboratorio(ficha_medica=registro_medico)),
        'oftalmologico_form': OftalmologicoForm(instance=Oftalmologico.objects.filter(ficha_medica=registro_medico).first() or Oftalmologico(ficha_medica=registro_medico)),
        'torax_form': ToraxForm(instance=Torax.objects.filter(ficha_medica=registro_medico).first() or Torax(ficha_medica=registro_medico)),
        'otros_examenes_form': OtrosExamenesClinicosForm(instance=OtrosExamenesClinicos.objects.filter(ficha_medica=registro_medico).first() or OtrosExamenesClinicos(ficha_medica=registro_medico)),
    }

    return render(request, 'medico/cargar_registro.html', context)


# medico_views
def ficha_medica_views(request, registro_id):
  

    # 🔹 Filtrar solo el registro médico correspondiente al torneo
    registro_medico = get_object_or_404(RegistroMedico, id=registro_id)
    print("El id del registro es : ",registro_id, registro_medico)
    jugador = registro_medico.jugador 

    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    # 🔹 Obtener la categoría, equipo y torneo en base al registro médico
    jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(
    jugador=jugador,
    categoria_equipo__categoria__torneo=registro_medico.torneo
    ).first()
    print("El jugador es : ", jugador)
    print("La categoria es : ", jugador_categoria_equipo.categoria_equipo.categoria.nombre)
    print("El equipo es : ", jugador_categoria_equipo.categoria_equipo.equipo.nombre)
    print("El torneo es : ", registro_medico.torneo.nombre)

    # Verificar si hay un perfil de médico asociado
    try:
        profile_id = request.session.get("user_profile_id")
        profile = Profile.objects.filter(id=profile_id).first()
        medico = Medico.objects.filter(profile=profile).first()
        if medico:
            rol_usuario = medico.profile.rol
        else:
            rol_usuario = None
    except Medico.DoesNotExist:
        rol_usuario = None

    print("Rol del usuario logueado:", rol_usuario)

    if request.method == 'POST':
        registro_medico_form = RegistroMedicoUpdateForm(request.POST, instance=registro_medico)
        if registro_medico_form.is_valid():
            registro_medico = registro_medico_form.save(commit=False)
            medico = Medico.objects.filter(profile=request.user.profile).first()
            if medico:
                registro_medico.medico = medico
            registro_medico.save()
            return redirect('ficha_medica', registro_id=registro_id)
    else:
        registro_medico_form = RegistroMedicoUpdateForm(instance=registro_medico)

    # 🔹 Filtrar antecedentes en base al jugador
    antecedentes = AntecedenteEnfermedades.objects.filter(jugador=jugador)

    # 🔹 Obtener solo los estudios médicos de este registro médico
    try:
        electro_basal = ElectroBasal.objects.get(ficha_medica=registro_medico)
    except ElectroBasal.DoesNotExist:
        electro_basal = None
    try:
        electro_esfuerzo = ElectroEsfuerzo.objects.get(ficha_medica=registro_medico)
    except ElectroEsfuerzo.DoesNotExist:
        electro_esfuerzo = None

    try:
        cardiovascular = Cardiovascular.objects.get(ficha_medica=registro_medico)
    except Cardiovascular.DoesNotExist:
        cardiovascular = None

    try:
        laboratorio = Laboratorio.objects.get(ficha_medica=registro_medico)
    except Laboratorio.DoesNotExist:
        laboratorio = None

    try:
        oftalmologico = Oftalmologico.objects.get(ficha_medica=registro_medico)
    except Oftalmologico.DoesNotExist:
        oftalmologico = None

    try:
        torax = Torax.objects.get(ficha_medica=registro_medico)
    except Torax.DoesNotExist:
        torax = None

    try:
        otros_examenes = OtrosExamenesClinicos.objects.get(ficha_medica=registro_medico)
    except OtrosExamenesClinicos.DoesNotExist:
        otros_examenes = None
    
    # 🔹 Convertir URLs relativas de imágenes en absolutas (solo si existen)
    if jugador_categoria_equipo and jugador_categoria_equipo.categoria_equipo.categoria.torneo.imagen:
        jugador_categoria_equipo.categoria_equipo.categoria.torneo.imagen_url = request.build_absolute_uri(
            jugador_categoria_equipo.categoria_equipo.categoria.torneo.imagen.url
        )

    if registro_medico.medico and registro_medico.medico.firma:
        registro_medico.medico.firma = request.build_absolute_uri(registro_medico.medico.firma.url)

    
    print(f"Registro Médico ID: {registro_medico.id}")
    print("ElectroBasal Datos:", electro_basal.__dict__ if electro_basal else "No encontrado")
    print("ElectroEsfuerzo Datos:", electro_esfuerzo.__dict__ if electro_esfuerzo else "No encontrado")
    print("Cardiovascular Datos:", cardiovascular.__dict__ if cardiovascular else "No encontrado")
    print("Laboratorio Datos:", laboratorio.__dict__ if laboratorio else "No encontrado")
    print("Oftalmológico Datos:", oftalmologico.__dict__ if oftalmologico else "No encontrado")
    print("Tórax Datos:", torax.__dict__ if torax else "No encontrado")
    print("Otros Exámenes Datos:", otros_examenes.__dict__ if otros_examenes else "No encontrado")


    # 🔹 Armar la información del jugador y su ficha médica
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

        # 🔹 Agregar la categoría, equipo y torneo del registro médico seleccionado
        'categoria': jugador_categoria_equipo.categoria_equipo.categoria.nombre if jugador_categoria_equipo else "Sin categoría",
        'equipo': jugador_categoria_equipo.categoria_equipo.equipo.nombre if jugador_categoria_equipo else "Sin equipo",
        'torneo': jugador_categoria_equipo.categoria_equipo.categoria.torneo.nombre if jugador_categoria_equipo else "Sin torneo",
        'imagen_torneo': jugador_categoria_equipo.categoria_equipo.categoria.torneo.imagen.url if jugador_categoria_equipo and jugador_categoria_equipo.categoria_equipo.categoria.torneo.imagen else None,
        'torneo_descripcion': jugador_categoria_equipo.categoria_equipo.categoria.torneo.descripcion if jugador_categoria_equipo else "Sin Descripcion",
        'torneo_direccion': jugador_categoria_equipo.categoria_equipo.categoria.torneo.direccion if jugador_categoria_equipo else "Sin Direccion",
        'torneo_telefono': jugador_categoria_equipo.categoria_equipo.categoria.torneo.telefono if jugador_categoria_equipo else "Sin Telefono",
        
        
        # 🔹 Obtener antecedentes del jugador
        'antecedentes': [
            {
                'fue_operado': ant.fue_operado,
                'toma_medicacion': ant.toma_medicacion,
                'estuvo_internado': ant.estuvo_internado,
                'sufre_hormigueos': ant.sufre_hormigueos,
                'es_diabetico': ant.es_diabetico,
                'es_asmatico': ant.es_asmatico,
                'es_alergico': ant.es_alergico,
                'alerg_observ': ant.alerg_observ,
                'antecedente_epilepsia': ant.antecedente_epilepsia,
                'desviacion_columna': ant.desviacion_columna,
                'dolor_cintura': ant.dolor_cintura,
                'fracturas': ant.fracturas,
                'dolores_articulares': ant.dolores_articulares,
                'falta_aire': ant.falta_aire,
                'traumatismos_craneo': ant.traumatismos_craneo,
                'dolor_pecho': ant.dolor_pecho,
                'perdida_conocimiento': ant.perdida_conocimiento,
                'presion_arterial': ant.presion_arterial,
                'muerte_subita_familiar': ant.muerte_subita_familiar,
                'enfermedad_cardiaca_familiar': ant.enfermedad_cardiaca_familiar,
                'soplo_cardiaco': ant.soplo_cardiaco,
                'abstenerce_competencia': ant.abstenerse_competencia,
                'antecedentes_coronarios_familiares': ant.antecedentes_coronarios_familiares,
                'fumar_hipertension_diabetes': ant.fumar_hipertension_diabetes,
                'consumo_cocaina_anabolicos': ant.consumo_cocaina_anabolicos,
                'cca_observaciones': ant.cca_observaciones,
            }
            for ant in antecedentes
        ],

        # 🔹 Agregar los formularios de estudios médicos específicos de este registro
        'electro_basal_form': ElectroBasalForm(instance=electro_basal) if electro_basal else None,
        'electro_esfuerzo_form': ElectroEsfuerzoForm(instance=electro_esfuerzo) if electro_esfuerzo else None,
        'cardiovascular_form': CardiovascularForm(instance=cardiovascular) if cardiovascular else None,
        'laboratorio_form': LaboratorioForm(instance=laboratorio) if laboratorio else None,
        'oftalmologico_form': OftalmologicoForm(instance=oftalmologico) if oftalmologico else None,
        'torax_form': ToraxForm(instance=torax) if torax else None,
        'otros_examenes_form': OtrosExamenesClinicosForm(instance=otros_examenes) if otros_examenes else None,
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
                            margin: 0;
                            padding: 0;
                        }}

                        /* Estilos del header */
                        header {{
                            display: flex;
                            align-items: center;
                        }}

                        /* Logo del torneo (MINIMIZADO) */
                        .logo img {{
                            max-width: 40px; /* ✅ Se redujo el tamaño al mínimo */
                            height: auto;
                            display: block;
                            margin: 0;
                            padding: 0;
                        }}

                        /* Títulos */
                        h1, h2, h3, h4 {{
                            color: #0056b3;
                            text-align: center;
                            font-weight: bold;
                            font-size: 10px;
                            margin: 0;
                            padding: 0;
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
                            background-color: #f7f7f7;
                            text-align: center;
                            font-size: 12px;
                            font-weight: bold;
                            padding: 5px;
                        }}

                        .card-body {{
                            line-height: 1.4;
                            font-size: 10px;
                        }}

                        /* Tablas - Espaciado mínimo */
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                            margin: 0;
                        }}

                        table th, table td {{
                            border: 1px solid #ddd;
                            text-align: left;
                            font-size: 9px;
                            padding: 2px; /* Se redujo el padding */
                            line-height: 1;
                        }}

                        table th {{
                            background-color: #f1f1f1;
                            font-weight: bold;
                        }}

                        /* Botones */
                        .btn {{
                            font-size: 10px;
                            font-weight: bold;
                            text-align: center;
                            color: white;
                            background-color: #007bff;
                            border: none;
                            padding: 3px 8px;
                            border-radius: 4px;
                            text-decoration: none;
                        }}

                        .btn:hover {{
                            background-color: #0056b3;
                        }}

                        /* Firma */
                        .img-fluid {{
                            display: block;
                            margin: auto;
                            max-width: 150px;
                            height: auto;
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
        'ocultar_header': True, 
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
    

@login_required
def seleccionar_apto(request):
    profile_id = request.session.get("user_profile_id")
    print(f"🔍 Profile ID: {profile_id}")
    profile = Profile.objects.filter(id=profile_id).first()
    
    medico = Medico.objects.filter(profile=profile).first() if profile else None
    print(f"🔍 Medico asociado al perfil: {medico}")

    context = {
        'search_dni': request.GET.get('search_dni', ''),
        'search_name': request.GET.get('search_name', ''),
        'profile': profile,
        'medico': medico,
    }

    return render(request, 'medico/seleccionar_apto.html', context)




# VISTAS PARA EL CUS DE LOS ESTUDIANTES

#vista cus_home

class CusHomeView(LoginRequiredMixin, ListView):
    model = Estudiante
    template_name = 'medico/cus_home.html'
    context_object_name = 'estudiantes'

    def get_queryset(self):
        queryset = Estudiante.objects.all()
        search_dni = self.request.GET.get('search_dni', '').strip()
        search_name = self.request.GET.get('search_name', '').strip()

        if not search_dni and not search_name:
            return Estudiante.objects.none()

        if search_dni:
            if search_dni.isdigit() and len(search_dni) == 8:
                queryset = queryset.filter(dni__icontains=search_dni)
            else:
                messages.error(self.request, "El DNI ingresado debe contener exactamente 8 números.")
                return Estudiante.objects.none()

        if search_name:
            palabras = search_name.split()
            consulta = Q()

            if len(palabras) == 1:
                consulta = Q(nombre__icontains=palabras[0]) | Q(apellido__icontains=palabras[0])
            elif len(palabras) >= 2:
                primer = palabras[0]
                segundo = palabras[1]
                consulta = (Q(nombre__icontains=primer) & Q(apellido__icontains=segundo)) | \
                           (Q(nombre__icontains=segundo) & Q(apellido__icontains=primer))

            queryset = queryset.filter(consulta)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_dni'] = self.request.GET.get('search_dni', '')
        context['search_name'] = self.request.GET.get('search_name', '')

        profile_id = self.request.session.get("user_profile_id")
        profile = Profile.objects.filter(id=profile_id).first()
        context['profile'] = profile

        if profile:
            context['medico'] = Medico.objects.filter(profile=profile).first()
        else:
            context['medico'] = None

        estudiantes_info = []

        if 'estudiantes' in context and context['estudiantes'].exists():
            for estudiante in context['estudiantes']:
                cus = Cus.objects.filter(estudiante=estudiante).first()
                
                info = {
                    'id': estudiante.id,
                    'dni': estudiante.dni,
                    'nombre': estudiante.nombre,
                    'apellido': estudiante.apellido,
                    'colegio': estudiante.colegio_activo(),
                    'estado': cus.estado if cus else 'Sin ficha',
                    'cus_id': cus.id if cus else None,
                    'tutor': f"{estudiante.tutor.profile.nombre} {estudiante.tutor.profile.apellido}" if estudiante.tutor else 'Sin tutor',
                }

                estudiantes_info.append(info)

        context['estudiantes_info'] = estudiantes_info
        context['cus_form'] = CusForm()

        return context


# vista para cargar_cus   

@login_required
def cus_update_view(request, cus_id):
    cus = get_object_or_404(Cus, id=cus_id)
    estudiante = cus.estudiante
    cus_form = CusForm(instance=cus)
    estudio_form = EstudioCusForm() 

    if request.method == 'POST':
        print(request.POST)  # Debug para ver qué botón fue presionado
        

        # Cargar estudio médico
        if 'cargar_estudio' in request.POST:
            estudio_form = EstudioCusForm(request.POST, request.FILES)
            if estudio_form.is_valid():
                estudio = estudio_form.save(commit=False)
                estudio.cus = cus
                estudio.save()
                messages.success(request, "✅ Estudio cargado exitosamente.")
            else:
                messages.error(request, "❌ Error al cargar el estudio.")
            return redirect('cus_update_view', cus_id=cus.id)

        # Guardar exámenes médicos
        elif 'guardar_examenes_medicos' in request.POST:
            forms_valid = True
            form_instances = {
                'examen_fisico_form': ExamenFisicoForm(request.POST, instance=ExamenFisico.objects.filter(cus=cus).first() or ExamenFisico(cus=cus)),
                'alimentacion_form': AlimentacionNutricionForm(request.POST, instance=AlimentacionNutricion.objects.filter(cus=cus).first() or AlimentacionNutricion(cus=cus)),
                'oftalmologico_form': ExamenOftalmologicoForm(request.POST, instance=ExamenOftalmologico.objects.filter(cus=cus).first() or ExamenOftalmologico(cus=cus)),
                'fono_form': ExamenFonoaudiologicoForm(request.POST, instance=ExamenFonoaudiologico.objects.filter(cus=cus).first() or ExamenFonoaudiologico(cus=cus)),
                'piel_form': ExamenPielForm(request.POST, instance=ExamenPiel.objects.filter(cus=cus).first() or ExamenPiel(cus=cus)),
                'odonto_form': ExamenOdontologicoForm(request.POST, instance=ExamenOdontologico.objects.filter(cus=cus).first() or ExamenOdontologico(cus=cus)),
                'cardio_form': ExamenCardiovascularForm(request.POST, instance=ExamenCardiovascular.objects.filter(cus=cus).first() or ExamenCardiovascular(cus=cus)),
                'respiratorio_form': ExamenRespiratorioForm(request.POST, instance=ExamenRespiratorio.objects.filter(cus=cus).first() or ExamenRespiratorio(cus=cus)),
                'abdomen_form': ExamenAbdomenForm(request.POST, instance=ExamenAbdomen.objects.filter(cus=cus).first() or ExamenAbdomen(cus=cus)),
                'genito_form': ExamenGenitourinarioForm(request.POST, instance=ExamenGenitourinario.objects.filter(cus=cus).first() or ExamenGenitourinario(cus=cus)),
                'endocrino_form': ExamenEndocrinologicoForm(request.POST, instance=ExamenEndocrinologico.objects.filter(cus=cus).first() or ExamenEndocrinologico(cus=cus)),
                'osteo_form': ExamenOsteoarticularForm(request.POST, instance=ExamenOsteoarticular.objects.filter(cus=cus).first() or ExamenOsteoarticular(cus=cus)),
                'neuro_form': ExamenNeurologicoForm(request.POST, instance=ExamenNeurologico.objects.filter(cus=cus).first() or ExamenNeurologico(cus=cus)),
                'comentario_form': ComentarioDerivacionForm(request.POST, instance=ComentarioDerivacion.objects.filter(cus=cus).first() or ComentarioDerivacion(cus=cus)),
                'recomendaciones_form': RecomendacionesForm(request.POST, instance=Recomendaciones.objects.filter(cus=cus).first() or Recomendaciones(cus=cus)),
            }

            for form in form_instances.values():
                if form.is_valid():
                    form.save()
                else:
                    forms_valid = False
                    print("❌ Error en examen:", form.errors)

            if forms_valid:
                messages.success(request, "✅ Exámenes médicos guardados correctamente.")
            else:
                messages.warning(request, "⚠️ Algunos exámenes tienen errores. Revisá los datos.")

            return redirect('cus_update_view', cus_id=cus.id)

        # Guardar el formulario principal del CUS
        elif 'guardar_ficha_cus' in request.POST:
            cus_form = CusForm(request.POST, instance=cus)

            antecedentes = AntecedentesCUS.objects.filter(estudiante=estudiante).first()
            if not antecedentes:
                antecedentes = AntecedentesCUS(estudiante=estudiante)
                antecedentes.save()

            if cus_form.is_valid():
                cus_form.save()
                messages.success(request, "✅ Certificado CUS guardado correctamente.")
            else:
                messages.error(request, "❌ Error al guardar el certificado CUS.")
            return redirect('cus_update_view', cus_id=cus.id)

    else:
        cus_form = CusForm(instance=cus)
        estudio_form = EstudioCusForm()

    antecedentes = estudiante.antecedentes if hasattr(estudiante, 'antecedentes') else None

    context = {
        'cus': cus,
        'estudiante': estudiante,
        'cus_form': cus_form,
        'estudio_cus_form': estudio_form,
        'antecedentes': antecedentes,
        'nombre': estudiante.nombre,
        'apellido': estudiante.apellido,
        'dni': estudiante.dni,
        'edad': estudiante.fecha_nacimiento,
        'tutor': f"{estudiante.tutor.profile.nombre} {estudiante.tutor.profile.apellido}" if estudiante.tutor else "-",
        'colegio': estudiante.colegio_activo(),
        'examen_fisico_form': ExamenFisicoForm(instance=ExamenFisico.objects.filter(cus=cus).first()),
        'alimentacion_form': AlimentacionNutricionForm(instance=AlimentacionNutricion.objects.filter(cus=cus).first()),
        'oftalmologico_form': ExamenOftalmologicoForm(instance=ExamenOftalmologico.objects.filter(cus=cus).first()),
        'fono_form': ExamenFonoaudiologicoForm(instance=ExamenFonoaudiologico.objects.filter(cus=cus).first()),
        'piel_form': ExamenPielForm(instance=ExamenPiel.objects.filter(cus=cus).first()),
        'odonto_form': ExamenOdontologicoForm(instance=ExamenOdontologico.objects.filter(cus=cus).first()),
        'cardio_form': ExamenCardiovascularForm(instance=ExamenCardiovascular.objects.filter(cus=cus).first()),
        'respiratorio_form': ExamenRespiratorioForm(instance=ExamenRespiratorio.objects.filter(cus=cus).first()),
        'abdomen_form': ExamenAbdomenForm(instance=ExamenAbdomen.objects.filter(cus=cus).first()),
        'genito_form': ExamenGenitourinarioForm(instance=ExamenGenitourinario.objects.filter(cus=cus).first()),
        'endocrino_form': ExamenEndocrinologicoForm(instance=ExamenEndocrinologico.objects.filter(cus=cus).first()),
        'osteo_form': ExamenOsteoarticularForm(instance=ExamenOsteoarticular.objects.filter(cus=cus).first()),
        'neuro_form': ExamenNeurologicoForm(instance=ExamenNeurologico.objects.filter(cus=cus).first()),
        'comentario_form': ComentarioDerivacionForm(instance=ComentarioDerivacion.objects.filter(cus=cus).first()),
        'recomendaciones_form': RecomendacionesForm(instance=Recomendaciones.objects.filter(cus=cus).first()),
    }

    return render(request, 'medico/cargar_cus.html', context)
# Manejo genérico para formularios del CUS


def manejar_formulario_cus(request, estudiante_id, cus_id, modelo, formulario_clase, template_name='medico/cargar_cus.html'):
    try:
        cus_id = int(cus_id)
    except ValueError:
        return HttpResponse("Error: cus_id debe ser un número entero.", status=400)

    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    cus = get_object_or_404(Cus, id=cus_id, estudiante=estudiante)

    instancia = modelo.objects.filter(cus=cus).first()

    if request.method == 'POST':
        formulario = formulario_clase(request.POST, request.FILES, instance=instancia)
        if formulario.is_valid():
            with transaction.atomic():
                instancia = formulario.save(commit=False)
                instancia.cus = cus
                instancia.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        formulario = formulario_clase(instance=instancia)

    return render(request, template_name, {
        'estudiante': estudiante,
        f'{modelo.__name__.lower()}_form': formulario,
    })

# Vistas específicas para cada formulario del CUS
def examen_fisico_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenFisico, ExamenFisicoForm)

def alimentacion_nutricion_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, AlimentacionNutricion, AlimentacionNutricionForm)

def examen_oftalmologico_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenOftalmologico, ExamenOftalmologicoForm)

def examen_fonoaudiologico_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenFonoaudiologico, ExamenFonoaudiologicoForm)

def examen_piel_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenPiel, ExamenPielForm)

def examen_odontologico_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenOdontologico, ExamenOdontologicoForm)

def examen_cardiovascular_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenCardiovascular, ExamenCardiovascularForm)

def examen_respiratorio_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenRespiratorio, ExamenRespiratorioForm)

def examen_abdomen_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenAbdomen, ExamenAbdomenForm)

def examen_genitourinario_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenGenitourinario, ExamenGenitourinarioForm)

def examen_endocrinologico_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenEndocrinologico, ExamenEndocrinologicoForm)

def examen_osteoarticular_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenOsteoarticular, ExamenOsteoarticularForm)

def examen_neurologico_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ExamenNeurologico, ExamenNeurologicoForm)

def estudio_cus_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, EstudioCus, EstudioCusForm)

def comentario_derivacion_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, ComentarioDerivacion, ComentarioDerivacionForm)

def recomendaciones_view(request, estudiante_id, cus_id):
    return manejar_formulario_cus(request, estudiante_id, cus_id, Recomendaciones, RecomendacionesForm)

@login_required
def cus_form_view(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    cus = Cus.objects.filter(estudiante=estudiante).first()
    if not cus:
        cus = Cus(estudiante=estudiante)

    if request.method == 'POST':
        form = CusForm(request.POST, instance=cus)
        if form.is_valid():
            instance = form.save(commit=False)

            # Asociar médico logueado si no está
            profile_id = request.session.get("user_profile_id")
            if profile_id and not instance.medico:
                from core.models import Profile
                from Medico.models import Medico
                profile = Profile.objects.filter(id=profile_id).first()
                if profile:
                    medico = Medico.objects.filter(profile=profile).first()
                    if medico:
                        instance.medico = medico

            instance.save()
            messages.success(request, "✅ Datos personales del CUS guardados correctamente.")
            return redirect('cus_update_view', cus_id=cus.id)
    else:
        form = CusForm(instance=cus)

    return render(request, 'medico/cus_form.html', {
        'form': form,
        'estudiante': estudiante
    })
    
@login_required
def cus_views(request, cus_id):
    cus = get_object_or_404(Cus, id=cus_id)
    estudiante = cus.estudiante
    examenes = {
    'Examen Físico': ExamenFisico.objects.filter(cus=cus).first(),
    'Alimentación y Nutrición': AlimentacionNutricion.objects.filter(cus=cus).first(),
    'Oftalmológico': ExamenOftalmologico.objects.filter(cus=cus).first(),
    'Fonoaudiológico': ExamenFonoaudiologico.objects.filter(cus=cus).first(),
    'Piel': ExamenPiel.objects.filter(cus=cus).first(),
    'Odontológico': ExamenOdontologico.objects.filter(cus=cus).first(),
    'Cardiovascular': ExamenCardiovascular.objects.filter(cus=cus).first(),
    'Respiratorio': ExamenRespiratorio.objects.filter(cus=cus).first(),
    'Abdomen': ExamenAbdomen.objects.filter(cus=cus).first(),
    'Genitourinario': ExamenGenitourinario.objects.filter(cus=cus).first(),
    'Endocrinológico': ExamenEndocrinologico.objects.filter(cus=cus).first(),
    'Osteoarticular': ExamenOsteoarticular.objects.filter(cus=cus).first(),
    'Neurológico': ExamenNeurologico.objects.filter(cus=cus).first(),
    'Comentario': ComentarioDerivacion.objects.filter(cus=cus).first(),
    'Recomendaciones': Recomendaciones.objects.filter(cus=cus).first(),
}
    
    for nombre, instancia in examenes.items():
        if instancia:
            print(f"✅ {nombre}: {instancia}")
        else:
            print(f"❌ {nombre}: No se encontró instancia")
        # Cargar formularios (solo visualización, no POST)
    
    
    
    contexto = {
        'cus': cus,
        'estudiante': estudiante,
        'tutor': f"{estudiante.tutor.profile.nombre} {estudiante.tutor.profile.apellido}" if estudiante.tutor else "-",
        'colegio': estudiante.colegio_activo(),
        'antecedentes': getattr(estudiante, 'antecedentes', None),
        'examen_fisico_form': ExamenFisicoForm(instance=ExamenFisico.objects.filter(cus=cus).first()),
        'alimentacion_form': AlimentacionNutricionForm(instance=AlimentacionNutricion.objects.filter(cus=cus).first()),
        'oftalmologico_form': ExamenOftalmologicoForm(instance=ExamenOftalmologico.objects.filter(cus=cus).first()),
        'fono_form': ExamenFonoaudiologicoForm(instance=ExamenFonoaudiologico.objects.filter(cus=cus).first() or ExamenFonoaudiologico(cus=cus)),
        'piel_form': ExamenPielForm(instance=ExamenPiel.objects.filter(cus=cus).first() or ExamenPiel(cus=cus)),
        'odonto_form': ExamenOdontologicoForm(instance=ExamenOdontologico.objects.filter(cus=cus).first() or ExamenOdontologico(cus=cus)),
        'cardio_form': ExamenCardiovascularForm(instance=ExamenCardiovascular.objects.filter(cus=cus).first() or ExamenCardiovascular(cus=cus)),
        'respiratorio_form': ExamenRespiratorioForm(instance=ExamenRespiratorio.objects.filter(cus=cus).first() or ExamenRespiratorio(cus=cus)),
        'abdomen_form': ExamenAbdomenForm(instance=ExamenAbdomen.objects.filter(cus=cus).first() or ExamenAbdomen(cus=cus)),
        'genito_form': ExamenGenitourinarioForm(instance=ExamenGenitourinario.objects.filter(cus=cus).first() or ExamenGenitourinario(cus=cus)),
        'endocrino_form': ExamenEndocrinologicoForm(instance=ExamenEndocrinologico.objects.filter(cus=cus).first() or ExamenEndocrinologico(cus=cus)),
        'osteo_form': ExamenOsteoarticularForm(instance=ExamenOsteoarticular.objects.filter(cus=cus).first() or ExamenOsteoarticular(cus=cus)),
        'neuro_form': ExamenNeurologicoForm(instance=ExamenNeurologico.objects.filter(cus=cus).first() or ExamenNeurologico(cus=cus)),
        'comentario_form': ComentarioDerivacionForm(instance=ComentarioDerivacion.objects.filter(cus=cus).first() or ComentarioDerivacion(cus=cus)),
        'recomendaciones_form': RecomendacionesForm(instance=Recomendaciones.objects.filter(cus=cus).first() or Recomendaciones(cus=cus)),
    
    }

# Repetí esto para cada formulario que aparece vacío
    if request.GET.get('descargar_pdf') == 'true':
        antecedentes = contexto['antecedentes']
        examen_fisico_form = contexto['examen_fisico_form']
        alimentacion_form = contexto['alimentacion_form']
        oftalmologico_form = contexto['oftalmologico_form']
        fono_form = contexto['fono_form']
        piel_form = contexto['piel_form']
        odonto_form = contexto['odonto_form']
        cardio_form = contexto['cardio_form']
        respiratorio_form = contexto['respiratorio_form']
        abdomen_form = contexto['abdomen_form']
        genito_form = contexto['genito_form']
        endocrino_form = contexto['endocrino_form']
        osteo_form = contexto['osteo_form']
        neuro_form = contexto['neuro_form']
        comentario_form = contexto['comentario_form']
        recomendaciones_form = contexto['recomendaciones_form']
        html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 12px;
            }}
            .section-title {{
                font-weight: bold;
                text-align: center;
                text-decoration: underline;
                margin: 20px 0 10px;
            }}
            .form-label {{
                font-weight: bold;
                display: inline-block;
                min-width: 180px;
            }}
            .yes-no-box {{
                display: inline-block;
                margin-left: 15px;
            }}
                .form-row {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 4px;
        }}
        .form-row span {{
            margin-right: 10px;
          }}
            </style>
    </head>
    <body>
        <div>


        <p class="section-title">CERTIFICADO ÚNICO DE SALUD (C.U.S.)</p>
        <p style="text-align: center;"><em>A llenar por profesional médico matriculado a nivel provincial - Validez por 1 año.</em></p>
        <p style="text-align: center;"><em>Para ingreso escolar, actividades de educación física curriculares y extracurriculares.</em></p>

        <div class="form-row">
            <span><strong>FECHA:</strong> {cus.fecha_de_llenado.strftime('%d/%m/%Y')}</span>
            <span><strong>D.N.I. Nº:</strong> {estudiante.dni}</span>
        </div>

        <div class="form-row">
            <span><strong>Apellido y Nombre:</strong> {estudiante.apellido} {estudiante.nombre}</span>
        </div>

        <div class="form-row">
            <span><strong>Fecha Nacimiento:</strong> {estudiante.fecha_nacimiento.strftime('%d/%m/%Y')}</span>
            <span><strong>Edad:</strong> {estudiante.edad}</span>
            <span><strong>Sexo:</strong> {getattr(estudiante, 'sexo', '-')}</span>
            <span><strong>Lugar de nacimiento:</strong> {getattr(estudiante, 'lugar_nacimiento', '-')}</span>
        </div>

        <div class="form-row">
            <span><strong>Domicilio:</strong> {estudiante.domicilio}</span>
            <span><strong>Localidad:</strong> {estudiante.localidad}</span>
            <span><strong>Tel:</strong> {getattr(estudiante, 'telefono', '-')}</span>
        </div>


            <hr>
           <div class="contenido">

    <!-- Columna izquierda: ANTECEDENTES -->
    <div class="columna">
        <p class="section-title">ANTECEDENTES</p>

        <p><strong>1. VACUNACIONES</strong></p>
        <p>
            Carnet: {'SI' if antecedentes.carnet_vacunacion else 'NO'} &nbsp;&nbsp;
            Completo: {'SI' if antecedentes.esquema_completo else 'NO'}
        </p>
        <p>Debe completar esquema con: {antecedentes.esquema_faltante or '-'}</p>

        <p><strong>2. ANTECEDENTES PATOLÓGICOS</strong></p>
        <p>Enfermedades Importantes: {antecedentes.enfermedades_importantes}</p>
        <p>Cirugías: {antecedentes.cirugias}</p>
        <p>Cardiovasculares: {antecedentes.cardiovasculares}</p>
        <p>Trauma funcional: {antecedentes.trauma_funcional}</p>
        <p>Alergias: {antecedentes.alergias}</p>
        <p>Oftalmológicos: {antecedentes.oftalmologicos}</p>
        <p>Auditivos: {antecedentes.auditivos}</p>
        <p>
            Diabetes: {'SI' if antecedentes.diabetes else 'NO'} &nbsp;&nbsp;
            Asma: {'SI' if antecedentes.asma else 'NO'} &nbsp;&nbsp;
            Chagas: {'SI' if antecedentes.chagas else 'NO'} &nbsp;&nbsp;
            Hipertensión: {'SI' if antecedentes.hipertension else 'NO'}
        </p>
        <p>
            Neurológico: {'SI' if antecedentes.neurologico else 'NO'} &nbsp;&nbsp;
            Otras: {antecedentes.otras}
        </p>

        <p><strong>3. CONDICIONES DE RIESGO</strong></p>
        <p>{antecedentes.condiciones_riesgo}</p>

        <p><strong>4. MEDICAMENTOS PRESCRIPTOS</strong></p>
        <p>{antecedentes.medicamentos_prescriptos}</p>

        <p><strong>5. DURANTE ACTIVIDAD FÍSICA PREVIA SUFRIÓ</strong></p>
        <p>
            Cansancio extremo: {'SI' if antecedentes.cansancio_extremo else 'NO'} &nbsp;&nbsp;
            Falta de aire: {'SI' if antecedentes.falta_aire else 'NO'} &nbsp;&nbsp;
            Pérdida de conocimiento: {'SI' if antecedentes.perdida_conocimiento else 'NO'}
        </p>
        <p>
            Palpitaciones: {'SI' if antecedentes.palpitaciones else 'NO'} &nbsp;&nbsp;
            Precordialgias: {'SI' if antecedentes.precordialgias else 'NO'} &nbsp;&nbsp;
            Cefaleas: {'SI' if antecedentes.cefaleas else 'NO'} &nbsp;&nbsp;
            Vómitos: {'SI' if antecedentes.vomitos else 'NO'}
        </p>
        <p>Otros síntomas: {antecedentes.otros}</p>
    </div>

   <div class="columna">
    <p class="section-title">EXÁMENES MÉDICOS</p>

    <p><strong>Examen Físico:</strong></p>
    <p>Peso: {examen_fisico_form.instance.peso} | Talla: {examen_fisico_form.instance.talla} | IMC: {examen_fisico_form.instance.imc}</p>
    <p>Diagnostico Antropometrico:: {examen_fisico_form.instance.diagnostico_antropometrico}</p>

    <p><strong>Alimentación y Nutrición:</strong></p>
    <p>Solicita plan especial: {'SI' if alimentacion_form.instance.solicita_plan_especial else 'NO'}</p>
    <p>Tipo de plan: {alimentacion_form.instance.tipo_plan}</p>

    <p><strong>Examen Oftalmológico:</strong></p>
    <p>Agudeza visual OD: {oftalmologico_form.instance.agudeza_visual_der} | OI: {oftalmologico_form.instance.agudeza_visual_izq}</p>
    <p>Usa anteojos: {'SI' if oftalmologico_form.instance.usa_anteojos else 'NO'}</p>
    <p>Otros: {oftalmologico_form.instance.otros}</p>

    <p><strong>Examen Fonoaudiológico:</strong></p>
    <p>{fono_form.instance.detalles}</p>

    <p><strong>Examen de Piel:</strong></p>
    <p>{piel_form.instance.detalles}</p>

    <p><strong>Examen Odontológico:</strong></p>
    <p>{odonto_form.instance.detalles}</p>

    <p><strong>Examen Cardiovascular:</strong></p>
    <p>Auscultación: {cardio_form.instance.auscultacion} | Soplos: {cardio_form.instance.soplos}</p>
    <p>R1: {cardio_form.instance.R1} | R2: {cardio_form.instance.R2}</p>
    <p>Tensión arterial: {cardio_form.instance.tension_arterial}</p>
    <p>Ruidos agregados: {cardio_form.instance.ruidos_agregados}</p>
    <p>Observaciones: {cardio_form.instance.observaciones}</p>

    <p><strong>Examen Respiratorio:</strong></p>
    <p>{respiratorio_form.instance.detalles}</p>

    <p><strong>Examen de Abdomen:</strong></p>
    <p>{abdomen_form.instance.detalles}</p>

    <p><strong>Examen Genitourinario:</strong></p>
    <p>Menarca: {'SI' if genito_form.instance.menarca else 'NO'}</p>
    <p>Turner: {'SI' if genito_form.instance.turner else 'NO'}</p>

    <p><strong>Examen Endocrinológico:</strong></p>
    <p>{endocrino_form.instance.detalles}</p>

    <p><strong>Examen Osteoarticular:</strong></p>
    <p>Columna normal: {'SI' if osteo_form.instance.columna_normal else 'NO'}</p>
    <p>Cifosis: {'SI' if osteo_form.instance.cifosis else 'NO'} | Lordosis: {'SI' if osteo_form.instance.lordosis else 'NO'} | Escoliosis: {'SI' if osteo_form.instance.escoliosis else 'NO'}</p>
    <p>Miembros superiores: {osteo_form.instance.miembros_superiores}</p>
    <p>Miembros inferiores: {osteo_form.instance.miembros_inferiores}</p>

    <p><strong>Examen Neurológico:</strong></p>
    <p>{neuro_form.instance.detalles}</p>

    <p><strong>Comentario / Derivación:</strong></p>
    <p>Comentarios y/o derivaciones: {comentario_form.instance.comentarios_derivaciones}</p>
    <p>Se recomienda: {comentario_form.instance.recomendaciones}</p>

    <p><strong>Recomendaciones:</strong></p>
    <p>{recomendaciones_form.instance.detalles}</p>
</div>
</div>

<!-- Sección inferior: CERTIFICADO MÉDICO -->
<div class="bloque-inferior">
    <p class="section-title">CERTIFICADO MÉDICO</p>
    <p><strong>Estado:</strong> {cus.estado}</p>
    <p><strong>Fecha de emisión:</strong> {cus.fecha_de_llenado.strftime('%d/%m/%Y')}</p>
    <p><strong>Fecha de vencimiento:</strong> {cus.fecha_caducidad.strftime('%d/%m/%Y')}</p>

    <p class="mt-3">
        Hago constar que <strong>{estudiante.apellido} {estudiante.nombre}</strong> se encuentra en condiciones para el ingreso escolar, la realización de actividades físicas curriculares y lo establecido en la Resolución M.E. 57 de acuerdo al examen clínico actual y en reposo practicado en la fecha.
    </p>

    <p class="fw-bold mt-2">
        ESTA DOCUMENTACIÓN ORIGINAL DEBE PERMANECER EN CUSTODIA Y CONSERVACIÓN LEGAL DE LA DIRECCIÓN DEL CENTRO EDUCATIVO, Y LA COPIA EN PODER DEL RESPONSABLE LEGAL DEL ALUMNO.
    </p>

    <p class="mt-4"><strong>Médico responsable:</strong> {cus.medico.profile.nombre} {cus.medico.profile.apellido}</p>
    <p><strong>Matrícula:</strong> {cus.medico.matricula}</p>
</div>
        </div>
    </body>
    </html>
    """

        pdf = HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cus_{estudiante.apellido}_{estudiante.nombre}.pdf"'
        return response

    return render(request, 'medico/cus_views.html', contexto)