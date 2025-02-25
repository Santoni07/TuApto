from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import ListView
from django.db.models import Q
from django.db import transaction
from weasyprint import HTML
from persona.models import Jugador,JugadorCategoriaEquipo
from RegistroMedico.models import RegistroMedico, AntecedenteEnfermedades
from django.contrib.auth.mixins import LoginRequiredMixin
from Medico.models import Medico
from RegistroMedico.forms import *
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import reverse

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

        try:
            context['medico'] = Medico.objects.get(profile=self.request.user.profile)
        except Medico.DoesNotExist:
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

def manejar_formulario_medico(request, jugador_id, modelo, formulario_clase, template_name='medico/medico_home.html'):
    """
    Función genérica para manejar formularios médicos.

    :param request: HTTP request object
    :param jugador_id: ID del jugador
    :param modelo: Modelo relacionado con el formulario
    :param formulario_clase: Clase del formulario
    :param template_name: Plantilla a renderizar
    :return: HttpResponse con el formulario renderizado o JSON si es AJAX
    """

    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

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
def electro_basal_view(request, jugador_id):
    return manejar_formulario_medico(request, jugador_id, ElectroBasal, ElectroBasalForm)

def electro_esfuerzo_view(request, jugador_id):
    return manejar_formulario_medico(request, jugador_id, ElectroEsfuerzo, ElectroEsfuerzoForm)

def otros_examenes_clinicos_view(request, jugador_id):
    return manejar_formulario_medico(request, jugador_id, OtrosExamenesClinicos, OtrosExamenesClinicosForm)

def cardiovascular_view(request, jugador_id):
    return manejar_formulario_medico(request, jugador_id, Cardiovascular, CardiovascularForm)

def laboratorio_view(request, jugador_id):
    return manejar_formulario_medico(request, jugador_id, Laboratorio, LaboratorioForm)

def torax_view(request, jugador_id):
    return manejar_formulario_medico(request, jugador_id, Torax, ToraxForm)

def oftalmologico_view(request, jugador_id):
    return manejar_formulario_medico(request, jugador_id, Oftalmologico, OftalmologicoForm)

# medico_update
""" def registro_medico_update_view(request, jugador_id):
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
 """

def registro_medico_update_view(request, registro_id):
    registro_medico = get_object_or_404(RegistroMedico, id=registro_id)
    jugador = registro_medico.jugador

    if request.method == 'POST':
        print(request.POST)  # Depuración: Verifica los valores enviados en el formulario
        registro_medico_form = RegistroMedicoUpdateForm(request.POST, instance=registro_medico)
        
        if registro_medico_form.is_valid():
            with transaction.atomic():
                registro_medico = registro_medico_form.save(commit=False)
                
                # Obtener al médico logueado
                medico = Medico.objects.filter(profile=request.user.profile).first()
                if medico:
                    registro_medico.medico = medico  # Asignar el médico logueado

                registro_medico.save()
                return redirect('registro_medico_update_view', registro_id=registro_id)
        else:
            print("Formulario no válido:", registro_medico_form.errors)  # Depuración

    else:
        registro_medico_form = RegistroMedicoUpdateForm(instance=registro_medico)

    jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(
    jugador=jugador,
    categoria_equipo__categoria__torneo=registro_medico.torneo
    ).first()
    # 🔹 Contexto con la información del jugador y su registro médico
    context = {
        'jugador': jugador,
        'registro_medico': registro_medico,
        'registro_medico_form': registro_medico_form,
        'nombre': jugador.persona.profile.nombre,
        'apellido': jugador.persona.profile.apellido,
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
            for estudio in EstudiosMedico.objects.filter(ficha_medica=registro_medico)
        ],
        'electro_basal_form': ElectroBasalForm(instance=ElectroBasal.objects.filter(ficha_medica=registro_medico).first()),
        'electro_esfuerzo_form': ElectroEsfuerzoForm(instance=ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()),
        'cardiovascular_form': CardiovascularForm(instance=Cardiovascular.objects.filter(ficha_medica=registro_medico).first()),
        'laboratorio_form': LaboratorioForm(instance=Laboratorio.objects.filter(ficha_medica=registro_medico).first()),
        'oftalmologico_form': OftalmologicoForm(instance=Oftalmologico.objects.filter(ficha_medica=registro_medico).first()),
        'torax_form': ToraxForm(instance=Torax.objects.filter(ficha_medica=registro_medico).first()),
        'otros_examenes_form': OtrosExamenesClinicosForm(instance=OtrosExamenesClinicos.objects.filter(ficha_medica=registro_medico).first()),
    }

    return render(request, 'medico/cargar_registro.html', context)
# medico_views



def ficha_medica_views(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)

    # 🔹 Filtrar solo el registro médico correspondiente al torneo
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    # 🔹 Obtener la categoría, equipo y torneo en base al registro médico
    jugador_categoria_equipo = JugadorCategoriaEquipo.objects.filter(jugador=jugador).first()

    # Verificar si hay un perfil de médico asociado
    try:
        medico = Medico.objects.get(profile=request.user.profile)
        rol_usuario = medico.profile.rol
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
            return redirect('ficha_medica', jugador_id=jugador_id)
    else:
        registro_medico_form = RegistroMedicoUpdateForm(instance=registro_medico)

    # 🔹 Filtrar antecedentes en base al jugador
    antecedentes = AntecedenteEnfermedades.objects.filter(jugador=jugador)

    # 🔹 Obtener solo los estudios médicos de este registro médico
    electro_basal = ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
    electro_esfuerzo = ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()
    cardiovascular = Cardiovascular.objects.filter(ficha_medica=registro_medico).first()
    laboratorio = Laboratorio.objects.filter(ficha_medica=registro_medico).first()
    oftalmologico = Oftalmologico.objects.filter(ficha_medica=registro_medico).first()
    torax = Torax.objects.filter(ficha_medica=registro_medico).first()
    otros_examenes = OtrosExamenesClinicos.objects.filter(ficha_medica=registro_medico).first()

    # 🔹 Convertir URLs relativas de imágenes en absolutas (solo si existen)
    if jugador_categoria_equipo and jugador_categoria_equipo.categoria_equipo.categoria.torneo.imagen:
        jugador_categoria_equipo.categoria_equipo.categoria.torneo.imagen_url = request.build_absolute_uri(
            jugador_categoria_equipo.categoria_equipo.categoria.torneo.imagen.url
        )

    if registro_medico.medico and registro_medico.medico.firma:
        registro_medico.medico.firma = request.build_absolute_uri(registro_medico.medico.firma.url)

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