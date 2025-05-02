
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from RegistroMedico.models import AntecedenteEnfermedades, RegistroMedico


from .forms import *
from .models import *



@login_required
def registrar_persona(request):
    profile_id = request.session.get("user_profile_id")
    profile = Profile.objects.filter(id=profile_id).first()

    if not profile:
        messages.error(request, "No se pudo identificar tu perfil.")
        return redirect('select_role')  # O a donde quieras redirigir si no hay perfil

    # Buscar o crear persona asociada al perfil
    persona = Persona.objects.filter(profile=profile).first()
    if not persona:
        persona = Persona(profile=profile)
        persona.save()

    jugador = Jugador.objects.filter(persona=persona).first()

    if request.method == 'POST':
        form_persona = PersonaForm(request.POST, instance=persona)
        form_jugador = JugadorForm(request.POST, instance=jugador) if jugador else JugadorForm(request.POST)

        if form_persona.is_valid() and form_jugador.is_valid():
            persona_guardada = form_persona.save(commit=False)
            persona_guardada.profile = profile
            persona_guardada.save()

            jugador_guardado = form_jugador.save(commit=False)
            jugador_guardado.persona = persona_guardada
            jugador_guardado.save()

            messages.success(request, "¡Datos guardados correctamente!")
            return redirect('seleccionar_categoria_equipo')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form_persona = PersonaForm(instance=persona)
        form_jugador = JugadorForm(instance=jugador) if jugador else JugadorForm()

    # Verificar si ya está completo
    registro_completo = all([
        persona.direccion,
        persona.telefono,
        jugador and jugador.grupo_sanguineo,
        JugadorCategoriaEquipo.objects.filter(jugador=jugador).exists() if jugador else False
    ])

    if registro_completo:
        return redirect('menu_jugador')

    context = {
        'form_persona': form_persona,
        'form_jugador': form_jugador,
        'persona': persona,
        'profile': profile,
        'jugador': jugador,
    }
    return render(request, 'persona/registrar_persona.html', context)
def fetch_categorias(request, torneo_id):
    try:
        print(f"Torneo seleccionado: {torneo_id}")
        categorias = Categoria.objects.filter(torneo_id=torneo_id).values('id', 'nombre')
        print(categorias)  # Para verificar qué categorías se obtienen
        return JsonResponse({'categorias': list(categorias)})
    except Exception as e:
        print(f"Error al obtener categorías: {e}")  # Para ver cualquier error
        return JsonResponse({'error': str(e)}, status=500)


def fetch_equipos(request, categoria_id):
    # Filtrar los equipos relacionados con la categoría especificada
    try:
        equipos = Equipo.objects.filter(categoria_equipos__categoria_id=categoria_id).values('id', 'nombre')
        print(equipos)
        return JsonResponse({'equipos': list(equipos)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


    print(f"Torneo seleccionado:")
    if request.method == 'POST':
        # Solicitud POST: Procesar el formulario
        print("Solicitud POST recibida")
        print(request.POST)
        torneo_id = request.POST.get('torneo')
        print(f"Torneo seleccionado: {torneo_id}")
        categoria_id = request.POST.get('categoria')
        equipo_id = request.POST.get('equipo')

        # Obtener la persona y el jugador
        persona = get_object_or_404(Persona, profile=request.user.profile)
        jugador = Jugador.objects.get(persona=persona)

        # Obtener la instancia de CategoriaEquipo
        categoria_equipo = get_object_or_404(CategoriaEquipo, categoria_id=categoria_id, equipo_id=equipo_id)

        # Crear la asociación en el modelo JugadorCategoriaEquipo
        JugadorCategoriaEquipo.objects.create(
            jugador=jugador,
            categoria_equipo=categoria_equipo  # Cambiado a la instancia de CategoriaEquipo
        )

        # Redirigir o mostrar un mensaje de éxito
        return redirect('registro_exitoso')  # O la URL a la que quieras redirigir

    else:
        # Solicitud GET: Cargar torneos y renderizar el formulario
        torneos = Torneo.objects.all()
        print(torneos)
        return render(request, 'persona/seleccionar_categoria_equipo.html', {'torneos': torneos})


@login_required
def seleccionar_categoria_equipo(request):
    if request.method == 'POST':
        torneo_id = request.POST.get('torneo')
        categoria_id = request.POST.get('categoria')
        equipo_id = request.POST.get('equipo')

        try:
            profile_id = request.session.get("user_profile_id")
            profile = get_object_or_404(Profile, id=profile_id)

            persona = get_object_or_404(Persona, profile=profile)
            jugador = get_object_or_404(Jugador, persona=persona)
            categoria_equipo = get_object_or_404(CategoriaEquipo, categoria_id=categoria_id, equipo_id=equipo_id)

            # Verificar si ya existe la relación para evitar IntegrityError duplicado
            if not JugadorCategoriaEquipo.objects.filter(jugador=jugador, categoria_equipo=categoria_equipo).exists():
                JugadorCategoriaEquipo.objects.create(jugador=jugador, categoria_equipo=categoria_equipo)

            return redirect('menu_jugador')

        except Exception as e:
            print(f"[ERROR selección equipo] {e}")
            return redirect('home')

    else:
        torneos = Torneo.objects.all()
        return render(request, 'persona/seleccionar_categoria_equipo.html', {'torneos': torneos})
def error_registro(request):
    return render(request, 'persona/error_registro.html')



@login_required
@never_cache
def menu_jugador(request):
    # Obtener el perfil del usuario logueado
    try:
        profile = Profile.objects.get(user=request.user, rol='jugador')
    except Profile.DoesNotExist:
        return redirect('select_role')

    # Obtener la persona asociada
    try:
        persona = Persona.objects.get(profile=profile)
        jugador = Jugador.objects.get(persona=persona)
    except Persona.DoesNotExist:
        return redirect('registrar_persona')
    except Jugador.DoesNotExist:
        return redirect('registrar_jugador')

    # Fichas médicas
    fichas_medicas = RegistroMedico.objects.filter(jugador=jugador).select_related('torneo')
    fichas_medicas_data = list(fichas_medicas)

    # Antecedentes
    antecedentes = AntecedenteEnfermedades.objects.filter(jugador=jugador).first()  # uno solo porque es OneToOneField

    # Categorías y Equipos
    jugador_categoria_equipos = JugadorCategoriaEquipo.objects.select_related(
        'categoria_equipo__categoria__torneo',
        'categoria_equipo__equipo'
    ).filter(jugador=jugador)

    # Construir info del jugador
    jugador_info = {
        'nombre': jugador.persona.profile.nombre,
        'apellido': jugador.persona.profile.apellido,
        'direccion': jugador.persona.direccion,
        'telefono': jugador.persona.telefono,
        'grupo_sanguineo': jugador.grupo_sanguineo,
        'cobertura_medica': jugador.cobertura_medica,
        'numero_afiliado': jugador.numero_afiliado,
        'categorias_equipo': []
    }

    for jugador_categoria in jugador_categoria_equipos:
        categoria_equipo = jugador_categoria.categoria_equipo
        torneo = categoria_equipo.categoria.torneo

        # Buscar ficha médica correspondiente a ese torneo
        ficha_medica_asociada = fichas_medicas.filter(torneo=torneo).first()

        categoria_info = {
            'nombre_categoria': categoria_equipo.categoria.nombre,
            'nombre_equipo': categoria_equipo.equipo.nombre,
            'torneo': {
                'nombre': torneo.nombre,
                'descripcion' : torneo.descripcion,
                'direccion': torneo.direccion if hasattr(torneo, 'direccion') else "No disponible",
                'telefono': torneo.telefono if hasattr(torneo, 'telefono') else "No disponible",
                'imagen' : torneo.imagen.url if torneo.imagen else None
            },
            'ficha_medica': ficha_medica_asociada
        }
        jugador_info['categorias_equipo'].append(categoria_info)

    context = {
        'persona': persona,
        'profile': profile,
        'jugador': jugador,
        'jugador_id': jugador.id,
        'jugador_info': jugador_info,
        'antecedentes': antecedentes,
        'ficha_medica': fichas_medicas,
        'ficha_medica_data': fichas_medicas_data,
    }

    return render(request, 'persona/menu_jugador.html', context)





def modificar_perfil(request):
    profile = request.user.profile
    persona = getattr(profile, 'persona', None)
    
    # Obtener el jugador asociado a la persona
    jugador = None
    if persona:
        jugador = getattr(persona, 'jugador', None)

    if request.method == 'POST':
        form_persona = PersonaForm(request.POST, instance=persona)
        form_jugador = JugadorForm(request.POST, instance=jugador)

        if form_persona.is_valid() and form_jugador.is_valid():
            form_persona.save()
            form_jugador.save()
            return redirect('menu_jugador')
    else:
        form_persona = PersonaForm(instance=persona)
        form_jugador = JugadorForm(instance=jugador)

    return render(request, 'persona/modificar_perfil.html', {
        'form_persona': form_persona,
        'form_jugador': form_jugador,  # Pasar el formulario del jugador al contexto
        'jugador': jugador  # Pasa el objeto jugador al contexto
    })


@login_required
def perfil(request):
    # Obtener el perfil activo desde la sesión
    profile_id = request.session.get("user_profile_id")
    profile = Profile.objects.filter(id=profile_id).first()

    if not profile:
        return HttpResponse("No se pudo cargar el perfil.", status=404)

    # Obtener la persona asociada al perfil (si existe)
    persona = getattr(profile, 'persona', None)

    # Obtener el jugador asociado a la persona (si existe)
    jugador = getattr(persona, 'jugador', None) if persona else None

    # Pasar profile, persona y jugador al contexto
    return render(request, 'persona/perfil.html', {
        'profile': profile,
        'persona': persona,
        'jugador': jugador,
    })

def cambiar_email(request):
    # Obtener el perfil del usuario actual
    profile = request.user.profile

    if request.method == 'POST':
        
        new_email = request.POST.get('email')

        
        user = request.user
        user.email = new_email
        
        
        user.username = new_email  

        user.save() 

        
        profile.email = new_email
        profile.save()  

        return redirect('perfil')  

    return render(request, 'persona/modificar_email.html', {'profile': profile})

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Contraseña Actual", widget=forms.PasswordInput, required=True)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):  # Verifica si la contraseña actual es correcta
            raise forms.ValidationError("La contraseña actual no es correcta.")
        return old_password

def cambiar_contraseña(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el nuevo password
            update_session_auth_hash(request, user)  # Mantener la sesión activa después de cambiar la contraseña
            messages.success(request, '¡Contraseña cambiada con éxito!')  # Agregar mensaje de éxito
            return redirect('perfil')  # Redirigir al perfil o donde desees
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'persona/modificar_contrasena.html', {'form': form})

# funcion para inscribirme en un nuevo torneo 
@login_required
def inscribirse_a_torneo(request):
    profile = get_object_or_404(Profile, user=request.user, rol='jugador')
    jugador = get_object_or_404(Jugador, persona__profile=profile)

    torneos_actuales_ids = RegistroMedico.objects.filter(jugador=jugador).values_list('torneo_id', flat=True)
    torneos_disponibles = Torneo.objects.exclude(id__in=torneos_actuales_ids)

    if request.method == 'POST':
        torneo_id = request.POST.get('torneo_id')
        categoria_id = request.POST.get('categoria_id')
        equipo_id = request.POST.get('equipo_id')

        if torneo_id and categoria_id and equipo_id:
            torneo = get_object_or_404(Torneo, id=torneo_id)
            categoria = get_object_or_404(Categoria, id=categoria_id, torneo=torneo)
            equipo = get_object_or_404(Equipo, id=equipo_id)

            categoria_equipo, created = CategoriaEquipo.objects.get_or_create(categoria=categoria, equipo=equipo)

            if not JugadorCategoriaEquipo.objects.filter(jugador=jugador, categoria_equipo=categoria_equipo).exists():
                JugadorCategoriaEquipo.objects.create(jugador=jugador, categoria_equipo=categoria_equipo)

            antecedente = get_object_or_404(AntecedenteEnfermedades, jugador=jugador)

            RegistroMedico.objects.create(
                jugador=jugador,
                torneo=torneo,
                estado='PROCESO',
                consentimiento_persona=True,
                observacion='Inscripción a torneo con selección dinámica'
            )

            return redirect('menu_jugador')
        else:
            # Si faltan datos, redireccionar o mostrar error
            return redirect('inscribirse_a_torneo')  # O podrías usar messages.error() y renderizar el formulario

    return render(request, 'persona/inscribirse_torneo.html', {
        'torneos_disponibles': torneos_disponibles
    })
