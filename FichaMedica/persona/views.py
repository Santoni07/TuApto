
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from RegistroMedico.models import AntecedenteEnfermedades, RegistroMedico


from .forms import *
from .models import *

""" def registrar_persona(request):
    profile = request.user.profile

    # Intentamos obtener la Persona asociada al profile del usuario
    persona, created = Persona.objects.get_or_create(profile=profile)

    if created:
        print(f"Persona creada: {persona}")
    else:
        print(f"Persona encontrada: {persona}")

    # Verificamos si los campos obligatorios de la persona están completos
    campos_completos = all([
        persona.direccion,
        persona.telefono,
    ])

    # Intentamos obtener el jugador asociado a la persona
    try:
        jugador = Jugador.objects.get(persona=persona)
        campos_jugador_completos = all([
            jugador.grupo_sanguineo,
        ])
    except Jugador.DoesNotExist:
        jugador = None  # Si no hay jugador, se establece en None
        campos_jugador_completos = False

    # Intentamos obtener la relación de equipo y categoría asociada al jugador
    jugador_equipo_categoria = None
    if jugador:
        try:
            jugador_equipo_categoria = JugadorCategoriaEquipo.objects.get(jugador=jugador)
            equipo_categoria_completo = True
        except JugadorCategoriaEquipo.DoesNotExist:
            equipo_categoria_completo = False
    else:
        equipo_categoria_completo = False

    # Verificamos si todos los campos obligatorios están completos
    if campos_completos and campos_jugador_completos and equipo_categoria_completo:
        return redirect('menu_jugador')  # Redirigir si ya está completo

    # Manejo de los formularios
    if request.method == 'POST':
        # Formularios para persona y jugador
        form_persona = PersonaForm(request.POST, instance=persona)
        form_jugador = JugadorForm(request.POST, instance=jugador) if jugador else JugadorForm(request.POST)

        if form_persona.is_valid() and form_jugador.is_valid():
            # Guardar la persona sin crear una nueva si ya existe
            persona_guardada = form_persona.save(commit=False)
            persona_guardada.profile = profile
            persona_guardada.save()

            # Guardar el jugador y asignar la persona
            jugador_guardado = form_jugador.save(commit=False)
            jugador_guardado.persona = persona_guardada
            jugador_guardado.save()

            return redirect('seleccionar_categoria_equipo')  # Redirigir al siguiente paso tras guardar
    else:
        form_persona = PersonaForm(instance=persona)
        form_jugador = JugadorForm(instance=jugador) if jugador else JugadorForm()

    context = {
        'form_persona': form_persona,
        'form_jugador': form_jugador,
        'persona': persona,
        'profile': profile,
        'jugador': jugador,
        'jugador_equipo_categoria': jugador_equipo_categoria,
    }
    return render(request, 'persona/registrar_persona.html', context)


 """



def registrar_persona(request):
    profile = request.user.profile

    # Obtener o crear la Persona asociada al perfil
    persona, created = Persona.objects.get_or_create(profile=profile)
    jugador = Jugador.objects.filter(persona=persona).first()

    if request.method == 'POST':
        form_persona = PersonaForm(request.POST, instance=persona)
        form_jugador = JugadorForm(request.POST, instance=jugador) if jugador else JugadorForm(request.POST)

        if form_persona.is_valid() and form_jugador.is_valid():
            # Guardar Persona
            persona_guardada = form_persona.save(commit=False)
            persona_guardada.profile = profile
            persona_guardada.save()

            # Guardar Jugador
            jugador_guardado = form_jugador.save(commit=False)
            jugador_guardado.persona = persona_guardada
            jugador_guardado.save()

            messages.success(request, "¡Datos guardados correctamente!")

            # Redirigir al siguiente paso
            return redirect('seleccionar_categoria_equipo')

        else:
            # Si hay errores en el formulario
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


def seleccionar_categoria_equipo(request):
    if request.method == 'POST':
        # Solicitud POST: Procesar el formulario
        print("Solicitud POST recibida")
        print(request.POST)

        torneo_id = request.POST.get('torneo')
        print(f"Torneo seleccionado: {torneo_id}")
        categoria_id = request.POST.get('categoria')
        equipo_id = request.POST.get('equipo')

        try:
            # Obtener la persona asociada al perfil del usuario
            persona = get_object_or_404(Persona, profile=request.user.profile)
            
            # Obtener el jugador asociado a esa persona
            jugador = get_object_or_404(Jugador, persona=persona)
            print(f"Jugador encontrado: {jugador.id}")
            
            # Obtener la instancia de CategoriaEquipo
            categoria_equipo = get_object_or_404(CategoriaEquipo, categoria_id=categoria_id, equipo_id=equipo_id)
            print(f"Categoría-Equipo encontrada: {categoria_equipo.id}")
            # Crear la asociación en el modelo JugadorCategoriaEquipo
            JugadorCategoriaEquipo.objects.create(
                jugador=jugador,
                categoria_equipo=categoria_equipo
            )

            # Redirigir o mostrar un mensaje de éxito
            return redirect('menu_jugador')  # O la URL a la que quieras redirigir

        except Jugador.DoesNotExist:
            print("Error: El jugador no existe para la persona.")
            return redirect('home')  # Redirige a una página de error o mostrar un mensaje adecuado
        except CategoriaEquipo.DoesNotExist:
            print("Error: La categoría o equipo no existe.")
            return redirect('home')  # Redirige a una página de error o mostrar un mensaje adecuado
        except IntegrityError as e:
            print(f"Error de integridad (clave foránea fallida): {e}")
            return redirect('home')  # Redirige a una página de error o mostrar un mensaje adecuado
        except Exception as e:
            print(f"Otro error ocurrió: {e}")
            return redirect('home')  # Redirige a una página de error o mostrar un mensaje adecuado

    else:
        # Solicitud GET: Cargar torneos y renderizar el formulario
        torneos = Torneo.objects.all()
        print("Torneos disponibles:", torneos)
        return render(request, 'persona/seleccionar_categoria_equipo.html', {'torneos': torneos})


def error_registro(request):
    return render(request, 'persona/error_registro.html')


@login_required
@never_cache
def menu_jugador(request):
    # Obtener el perfil del usuario logueado
    profile = request.user.profile

    # Intentar obtener la Persona asociada al profile del usuario
    try:
        persona = Persona.objects.get(profile=profile)
        jugador = Jugador.objects.get(persona=persona)
    except Persona.DoesNotExist:
        return redirect('registrar_persona')
    except Jugador.DoesNotExist:
        return redirect('registrar_jugador')

    # Obtener la ficha médica del jugador
    try:
        ficha_medica = RegistroMedico.objects.get(jugador=jugador)
    except RegistroMedico.DoesNotExist:
        ficha_medica = None  # O maneja según lo que desees
       # Si no hay ficha médica, definir una estructura vacía para evitar errores en la plantilla
    ficha_medica_data = {
        'estado': ficha_medica.estado if ficha_medica else "No disponible",
        'consentimiento_persona': ficha_medica.consentimiento_persona if ficha_medica else False
    }
    # Obtener los antecedentes usando la ficha médica
    antecedentes = AntecedenteEnfermedades.objects.filter(idfichaMedica=ficha_medica)

    # Obtener las categorías, equipos y torneos relacionados al jugador
    jugador_categoria_equipos = JugadorCategoriaEquipo.objects.select_related(
        'categoria_equipo__categoria__torneo',
        'categoria_equipo__equipo'
    ).filter(jugador=jugador)

    # Crear una estructura para almacenar la información del jugador, categorías, equipos y torneos
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

    # Iterar sobre las categorías y equipos asociados al jugador
    for jugador_categoria in jugador_categoria_equipos:
        categoria_equipo = jugador_categoria.categoria_equipo
        torneo = categoria_equipo.categoria.torneo

        categoria_info = {
            'nombre_categoria': categoria_equipo.categoria.nombre,
            'nombre_equipo': categoria_equipo.equipo.nombre,
            'torneo': torneo.nombre
        }
        jugador_info['categorias_equipo'].append(categoria_info)

    # Pasar el contexto necesario a la plantilla
    context = {
        'persona': persona,
        'profile': profile,
        'jugador': jugador,
        'jugador_id': jugador.id,
        'jugador_info': jugador_info,
        'antecedentes': antecedentes,  # Incluir antecedentes en el contexto
        'ficha_medica': ficha_medica,
        'ficha_medica_data':ficha_medica_data,
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

def perfil(request):
    # Obtener el perfil del usuario actual
    profile = request.user.profile

    # Obtener la persona asociada al perfil (si existe)
    persona = getattr(profile, 'persona', None)

    # Obtener el jugador asociado a la persona (si existe)
    jugador = None
    if persona:
        jugador = getattr(persona, 'jugador', None)

    # Pasar profile, persona y jugador al contexto
    return render(request, 'persona/perfil.html', {
        'profile': profile,  # Pasamos el perfil
        'persona': persona,  # Pasamos la persona
        'jugador': jugador,  # Pasamos el jugador (si existe)
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