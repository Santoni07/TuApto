from django.shortcuts import redirect, render

from estudiante.models import Tutor
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
from django import forms
from Medico.models import Medico,Documentos

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
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'Usuario o contraseña incorrectos.')
                return redirect('login')

            user = authenticate(request, username=user.username, password=password)

            if user:
                return login_user_and_redirect(request, user)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
                return redirect('login')
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})


@login_required
def check_session(request):
    session_key = request.session.session_key

    if not session_key:
        return JsonResponse({'session_expired': True})

    try:
        session = Session.objects.get(session_key=session_key)

        if session.expire_date < now():
            return JsonResponse({'session_expired': True})

        return JsonResponse({'session_expired': False})

    except Session.DoesNotExist:
        return JsonResponse({'session_expired': True})


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

    profiles = Profile.objects.filter(user=user)
    if not profiles.exists():
        print("❌ No se encontró un perfil para este usuario.")
        return redirect('login')

    if profiles.count() > 1:
        return redirect('select_role')

    profile = profiles.first()
    print("Usuario autenticado con rol:", profile.rol)

    request.session['user_profile_id'] = profile.id

    if profile.rol == 'estudiante':
        tutor_asociado = Tutor.objects.filter(profile=profile).exists()
        if not tutor_asociado:
            return redirect('cargar_tutor')
        return redirect('menu_estudiante')

    # 🔍 Verificación especial para médicos
    if profile.rol == 'medico':
        try:
            medico = Medico.objects.get(profile=profile)
        except Medico.DoesNotExist:
            print("❌ No se encontró el perfil médico.")
            return redirect('login')

        try:
            doc = medico.documentacion
            if not (doc.certificado_matricula and doc.certificado_firma_electronica and doc.contrato_aceptado):
                print("⚠️ Faltan documentos obligatorios del médico.")
                return redirect('cargar_documentacion')
        except Documentos.DoesNotExist:
            print("⚠️ El médico no tiene documentación cargada.")
            return redirect('cargar_documentacion')

        return redirect('seleccionar_apto')

    if profile.rol == 'general':
        return redirect('menu_jugador')
    elif profile.rol == 'representante':
        return redirect('representante_home')
    elif profile.rol == 'colegio':
        return redirect('colegio_home')
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

            # 🔹 Guardar el perfil en la sesión antes de redirigir
            request.session["user_profile_id"] = profile.id
            request.session["user_profile_rol"] = profile.rol

            # 🔄 Redirección según el rol seleccionado
            if profile.rol == "jugador":
                return redirect("menu_jugador")
            elif profile.rol == "estudiante":
                return redirect("menu_estudiante")  # Redirige a home_estudiante, no a menu_estudiante directamente
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
"""
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
            print("❌ Errores del formulario:", user_form.errors)
            messages.error(request, "Hubo un error en el formulario. Verifica los datos ingresados.")

    # Si hay error o es GET, renderiza el formulario correspondiente
    template = "account/register.html" if user_role == "jugador" else "account/estudiante/register.html"
    return render(request, template, {'user_form': UserRegistrationForm()}) """



def preparar_formulario_existente(email, rol):
    form = UserRegistrationForm(initial={'email': email}, rol=rol)
    campos_ocultos = ['nombre', 'apellido', 'dni', 'fecha_nacimiento', 'password2']
    for campo in campos_ocultos:
        form.fields[campo].widget = forms.HiddenInput()
        form.fields[campo].required = False
        form.fields[campo].widget.attrs['readonly'] = True
    return form

def register(request):
    print(f"📥 Request recibido: {request.method} en {request.path}")

    user_role = "jugador"
    if request.path == "/account/register_alumnos/":
        user_role = "estudiante"

    # ✅ VALIDACIÓN ANTES DE MOSTRAR EL FORMULARIO COMPLETO
    if request.method == 'GET' and 'email' in request.GET:
        email = request.GET.get('email')
        user = User.objects.filter(email=email).first()

        print(f"rol del usuario", user)

        if user:
            if Profile.objects.filter(user=user, rol=user_role).exists():
                messages.error(request, f"Ya estás registrado como {user_role}. Iniciá sesión para continuar.")
                return redirect('login')

            # Si el usuario existe pero no con este rol, mostrar solo campo de contraseña
            form = preparar_formulario_existente(email, user_role)
            template = "account/register.html" if user_role == "jugador" else "account/estudiante/register.html"
            return render(request, template, {
                'verificar_password': True,
                'email': email,
                'user_form': form  # ✅ acá usás el form reducido
            })

    # 🧾 Registro POST
    if request.method == 'POST':
        print("📨 Se recibió POST")
        print("📥 POST DATA:", request.POST)
        email = request.POST.get('email')
        password = request.POST.get('password1')

        try:
            user_existente = User.objects.get(email=email)
            print("⚠️ Ya existe un usuario con ese email")

            user_auth = authenticate(request, username=user_existente.username, password=password)

            if user_auth is None:
                messages.error(request, "Contraseña incorrecta para el email proporcionado.")
                form = preparar_formulario_existente(email, user_role)
                form.fields['email'].initial = ''
                return render(
                    'account/register.html' if user_role == 'jugador' else 'account/estudiante/register.html',
                    {'user_form': form}
                )

            if Profile.objects.filter(user=user_existente, rol=user_role).exists():
                messages.error(request, f"Ya estás registrado en esta sección como {user_role}. Por favor, iniciá sesión.")
                return redirect('login')

            # 🔄 Heredar datos de otro perfil si existe
            # Buscar cualquier otro perfil existente del usuario (sin filtrar por rol)
            otro_perfil = Profile.objects.filter(user=user_existente).first()

            nombre = request.POST.get('nombre') or (otro_perfil.nombre if otro_perfil else '')
            apellido = request.POST.get('apellido') or (otro_perfil.apellido if otro_perfil else '')
            dni = request.POST.get('dni') or (otro_perfil.dni if otro_perfil else '')
            fecha_nacimiento = request.POST.get('fecha_nacimiento') or (otro_perfil.fecha_nacimiento if otro_perfil else None)

            profile = Profile.objects.create(
                user=user_existente,
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                fecha_nacimiento=fecha_nacimiento,
                email=email,
                rol=user_role
            )
            request.session['user_profile_id'] = profile.id
            return redirect('select_role')

        except User.DoesNotExist:
            form = UserRegistrationForm(request.POST, rol=user_role)
            if form.is_valid():
                user, profile = form.save()
                request.session['user_profile_id'] = profile.id
                return redirect('select_role')
            else:
                print("❌ Errores del formulario:", form.errors)
                messages.error(request, "Error en el registro. Verifica los datos.")
    else:
        form = UserRegistrationForm(rol=user_role)
        form.fields['email'].initial = ''

    template = "account/register.html" if user_role == "jugador" else "account/estudiante/register.html"
    return render(request, template, {'user_form': form})

def verificar_email(request):
    email = request.GET.get('email')
    rol_deseado = request.GET.get('rol')  # opcional, 'jugador', 'estudiante', etc.
    data = {'existe': False, 'tiene_rol': False}

    if email:
        try:
            user = User.objects.get(email=email)
            data['existe'] = True
            print(f"Usuario encontrado: {user.email}")

            perfiles = Profile.objects.filter(user=user)
            if perfiles.exists():
                if rol_deseado:
                    perfil_rol = perfiles.filter(rol=rol_deseado).first()
                    if perfil_rol:
                        data['tiene_rol'] = True
                        data['rol'] = perfil_rol.rol
                        print(f"Ya tiene rol {rol_deseado}")
                    else:
                        print(f"El usuario no tiene el rol {rol_deseado}")
                else:
                    primer_perfil = perfiles.first()
                    data['rol'] = primer_perfil.rol
                    print(f"Rol del primer perfil encontrado: {primer_perfil.rol}")
            else:
                print("El usuario no tiene perfiles asociados.")

        except User.DoesNotExist:
            print("No se encontró el usuario con ese email.")
        except Exception as e:
            print(f"Error inesperado: {str(e)}")

    return JsonResponse(data)



def verificar_dni(request):
    dni = request.GET.get('dni', None)
    data = {
        'existe': False
    }
    if dni and Profile.objects.filter(dni=dni).exists():
        data['existe'] = True
    return JsonResponse(data)
