from django.shortcuts import redirect, render
from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.contrib.auth import logout
from django.utils.timezone import now
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
                    elif profile.rol == 'estudiante':
                        return redirect('menu_estudiante')
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



def logout_view(request):
    logout
    return redirect('core/home.html')

def terminos_condiciones(request):
    return render(request, 'account/terminos_condiciones.html')


def recover_Password(request):
    return render(request, 'account/password_change_form.html')


def register(request):
    print(f"📥 Request recibido: {request.method} en {request.path}")  # Depuración

    user_role = "jugador"  # Valor predeterminado

    if request.path == "/account/register_alumnos/":
        user_role = "estudiante"

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user, profile = user_form.save(commit=False)  # Guardar sin confirmar aún

            # Guardamos usuario y perfil en la base de datos
            user.save()
            profile.user = user
            profile.rol = user_role  # Asignamos el rol dinámicamente
            profile.email = user.email  # Aseguramos que el email en Profile sea igual al del User
            profile.save()

            print(f"✅ Usuario registrado: {user.email} con rol {profile.rol}")

            # Mensaje de éxito
            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")

            # 🔹 Redirección única a register_done.html
            return render(request, 'account/register_done.html', {'new_user': user.email})

        else:
            messages.error(request, "Hubo un error en el formulario. Verifica los datos ingresados.")

    # Si es GET o hay errores, renderiza el formulario correspondiente
    template = "account/register.html" if user_role == "jugador" else "account/estudiante/register.html"
    return render(request, template, {'user_form': UserRegistrationForm()})

