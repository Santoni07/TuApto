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
from django.contrib.auth.models import User
from .models import Profile

@login_required
def dashboard(request):
    return redirect('persona/registrar')


@never_cache
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = cd['email']
            password = cd['password']

            # 🔍 Buscar todos los usuarios con este email (puede haber más de uno)
            users = User.objects.filter(email=email)
            print(f"El usuario es : ", users)
            if not users.exists():
                messages.error(request, 'Usuario o contraseña incorrectos. Intente nuevamente.')
                
                return redirect('login')

            # 👥 Si hay más de un usuario con el mismo email, pedir que elija el rol
            if users.count() > 1:
                roles = Profile.objects.filter(user__in=users).values_list('rol', flat=True)
                return render(request, 'account/select_role.html', {'email': email, 'roles': roles})

            # 🔐 Si solo hay un usuario, autenticamos normalmente
            user = authenticate(request, username=users[0].username, password=password)

            if user:
                if user.is_active:
                    return login_user_and_redirect(request, user)
                else:
                    return HttpResponse('El usuario no está activo')

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



# Función para generar usernames únicos combinando email y rol
def generate_unique_username(email, role):
    return f"{email}_{role}"


def login_user_and_redirect(request, user):
    login(request, user)

    # 🛠 Obtener el perfil correcto basado en el rol
    profiles = Profile.objects.filter(user=user)

    if not profiles.exists():
        print("❌ No se encontró un perfil para este usuario.")
        return redirect('login')

    # 🛠 Si el usuario tiene más de un perfil, redirigirlo a una pantalla de selección de rol
    if profiles.count() > 1:
        return redirect('select_role')

    # 🛠 Si solo tiene un perfil, lo usamos directamente
    profile = profiles.first()
    print("Usuario autenticado con rol:", profile.rol)

    # 🔄 Redirección condicional según el rol
    if profile.rol == 'medico':
        return redirect('medico_home')
    elif profile.rol == 'general':
        return redirect('menu_jugador')
    elif profile.rol == 'representante':
        return redirect('representante_home')
    elif profile.rol == 'jugador':
        return redirect('menu_jugador')
    elif profile.rol == 'estudiante':
        return redirect('menu_estudiante')
    else:
        return redirect('home')


@login_required
def select_role(request):
    user = request.user  # Asegurar que la sesión está activa
    profiles = Profile.objects.filter(user=user)

    print(f"👤 Usuario: {user.email}, Perfiles encontrados: {profiles}")

    if not profiles.exists():
        print("❌ No hay perfiles asociados al usuario, redirigiendo al login")
        return redirect('login')

    if request.method == "POST":
        selected_role = request.POST.get("role")
        print(f"🔄 Usuario seleccionó el rol: {selected_role}")

        try:
            profile = profiles.get(rol=selected_role)
            print(f"✅ Redirigiendo a menú de {profile.rol}")

            if profile.rol == "jugador":
                return redirect("menu_jugador")
            elif profile.rol == "estudiante":
                return redirect("menu_estudiante")
            elif profile.rol == "medico":
                return redirect("medico_home")
            elif profile.rol == "representante":
                return redirect("representante_home")
            else:
                return redirect("home")
        except Profile.DoesNotExist:
            print("❌ Error: Perfil no encontrado para este rol.")
            return redirect("select_role")

    return render(request, "account/select_role.html", {"profiles": profiles})

def register(request):
    print(f"📥 Request recibido: {request.method} en {request.path}")  # Depuración

    user_role = "jugador"  # Valor por defecto

    if request.path == "/account/register_alumnos/":
        user_role = "estudiante"

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            email = user_form.cleaned_data['email']
            username = generate_unique_username(email, user_role)

            # 🔍 Verificar si ya existe una cuenta con este email + rol
            if User.objects.filter(username=username).exists():
                messages.error(request, "Ya existe una cuenta con este rol y email. Usa otro rol o inicia sesión.")
                return redirect('register')

            # ✅ Crear el usuario correctamente
            user = User.objects.create_user(
                username=username,
                email=email,
                password=user_form.cleaned_data['password1']
            )
            user.save()  # Guarda el usuario en la base de datos

            # ✅ Crear el perfil y asegurarse de que se guarde correctamente
            profile = Profile.objects.create(
                user=user,
                nombre=user_form.cleaned_data['nombre'],
                apellido=user_form.cleaned_data['apellido'],
                dni=user_form.cleaned_data['dni'],
                fecha_nacimiento=user_form.cleaned_data['fecha_nacimiento'],
                email=email,
                rol=user_role  # Asignar rol dinámicamente
            )
            profile.save()  # Guarda el perfil en la base de datos

            print(f"✅ Usuario registrado: {user.email} con rol {profile.rol}")

            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return render(request, 'account/register_done.html', {'new_user': user.email})

        else:
            messages.error(request, "Hubo un error en el formulario. Verifica los datos ingresados.")

    # Si hay error o es GET, renderiza el formulario correspondiente
    template = "account/register.html" if user_role == "jugador" else "account/estudiante/register.html"
    return render(request, template, {'user_form': UserRegistrationForm()})