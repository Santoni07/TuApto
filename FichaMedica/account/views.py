from django.shortcuts import redirect, render
from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.contrib.auth import logout
from django.utils.timezone import now

from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib import messages
from persona.models import Persona, Jugador, JugadorCategoriaEquipo  

@login_required
def dashboard(request):
    return redirect('persona/registrar')

@never_cache
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, email=cd['email'], password=cd['password'])

            print(user)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    profile = user.profile
                    print("Usuario autenticado:", profile.rol)

                    # ✅ Verificar si el registro ya está completo
                    try:
                        persona = Persona.objects.get(profile=profile)
                        jugador = Jugador.objects.get(persona=persona)
                        equipo_categoria = JugadorCategoriaEquipo.objects.filter(jugador=jugador).exists()

                        registro_completo = all([
                            persona.direccion,
                            persona.telefono,
                            jugador.grupo_sanguineo,
                            equipo_categoria
                        ])
                    except (Persona.DoesNotExist, Jugador.DoesNotExist):
                        registro_completo = False
                    print("Rol del usuario : ", profile.rol)
                    # 🔄 Redirección condicional
                    if profile.rol == 'medico':
                        return redirect('medico_home')
                    elif profile.rol == 'general':
                        if registro_completo:
                            return redirect('menu_jugador')  # Si está completo, va al menú del jugador
                        else:
                            return redirect('registrar_persona')  # Si falta algo, sigue en registrar_persona
                    elif profile.rol == 'representante':
                        return redirect('representante_home')
                    elif profile.rol == 'jugador':
                        return redirect('menu_jugador')
                    else:
                        return redirect('home')

                else:
                    return HttpResponse('El usuario no está activo')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos. Intente nuevamente.')
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

@login_required
def check_session(request):
    try:
        session_key = request.session.session_key
        if not session_key:
            # La sesión no existe
            return JsonResponse({'session_expired': True})

        # Obtener la sesión actual
        session = Session.objects.get(session_key=session_key)
        
        # Verificar si la sesión ha expirado
        if session.expire_date < now():
            return JsonResponse({'session_expired': True})

        return JsonResponse({'session_expired': False})
    except Session.DoesNotExist:
        # Si la sesión no existe o es inválida
        return JsonResponse({'session_expired': True}, status=401)


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Guardar el usuario y su perfil
            user_form.save()  # Guarda tanto el usuario como el perfil asociado
            return render(request, 'account/register_done.html', {'new_user': user_form.cleaned_data['email']})
    else:
        user_form = UserRegistrationForm()

    # Mover este render fuera del bloque else, así se ejecuta tanto para GET como en caso de errores de validación
    return render(request, 'account/register.html', {'user_form': user_form})

def logout_view(request):
    logout
    return redirect('core/home.html')




def recover_Password(request):
    return render(request, 'account/password_change_form.html')