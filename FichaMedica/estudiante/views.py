from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import AntecedentesCUS, Estudiante, EstudianteColegio, Tutor, Colegio
from .forms import AntecedentesCUSForm, EstudianteForm, TutorForm
from account.models import Profile
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def home_estudiante(request):
    # 📌 Obtener el perfil del usuario autenticado desde la sesión
    profile_id = request.session.get('user_profile_id')
    
    profile = Profile.objects.filter(id=profile_id, rol="estudiante").first()
    print(f"Perfil del usuario: {profile}")

    if not profile:
        messages.error(request, "Error: No tienes un perfil de estudiante.")
        return redirect('home')

    # 🔎 Verificar si el perfil tiene un tutor asociado
    tutor_asociado = Tutor.objects.filter(profile=profile).exists()

    if not tutor_asociado:
        messages.warning(request, "Debes completar la información del tutor antes de continuar.")
        return redirect('cargar_tutor')  # ❌ Si no tiene tutor, redirigir a cargar tutor

    # ✅ Si tiene tutor, mostrar el menú del estudiante
    return render(request, 'estudiante/menu_estudiante.html')


def cargar_estudiante(request):
    # 📌 Verificar que el usuario tiene un tutor asociado
    profile_id = request.session.get("user_profile_id")
    print(f"🔍 Verificando perfil del usuario con ID: {profile_id}")
    
    if not profile_id:
        messages.error(request, "Error: No tienes un perfil de tutor seleccionado.")
        return redirect("home")

    # 🔍 Obtener el tutor asociado al perfil del usuario
    tutor = Tutor.objects.filter(profile_id=profile_id).first()
    print(f"🔍 Tutor asociado al perfil: {tutor}")
    
    if not tutor:
        messages.error(request, "Debes completar la información del tutor antes de agregar estudiantes.")
        return redirect("cargar_tutor")

    if request.method == 'POST':
        print("📩 Recibida solicitud POST con datos:", request.POST)  # 🚀 Depuración
        form = EstudianteForm(request.POST)
        
        if form.is_valid():
            print("✅ Formulario válido. Creando estudiante...")  # 🚀 Depuración
            # 🛠 Crear el estudiante y asociarlo al tutor
            estudiante = form.save(commit=False)
            estudiante.tutor = tutor  # Asociamos al tutor actual
            estudiante.save()
            print(f"✅ Estudiante guardado: {estudiante.nombre} {estudiante.apellido}, ID: {estudiante.id}")

            # 📌 Asociar el estudiante al colegio seleccionado
            colegio_id = request.POST.get("colegio")  # Obtener el ID del colegio desde el formulario
            colegio = Colegio.objects.filter(id=colegio_id).first()
            if colegio:
                EstudianteColegio.objects.create(estudiante=estudiante, colegio=colegio, activo=True)
                print(f"🏫 Estudiante asociado al colegio: {colegio.nombre}")

            messages.success(request, "Estudiante registrado con éxito.")
            return redirect("listar_estudiantes")  # 🔄 Redirigir a la lista de estudiantes
        
        else:
            print("❌ ERROR: Formulario no válido")
            print("❌ Errores del formulario:", form.errors)  # Muestra los errores en la terminal
            messages.error(request, "Error en el formulario. Verifica los datos ingresados.")
    
    else:
        form = EstudianteForm()

    colegios = Colegio.objects.all()  # Obtener todos los colegios disponibles
    return render(request, "estudiante/cargar_estudiante.html", {"form": form, "colegios": colegios})

def listar_estudiantes(request):
    profile_id = request.session.get("user_profile_id")

    if not profile_id:
        messages.error(request, "Error: No tienes un perfil de tutor seleccionado.")
        return redirect("home")

    tutor = Tutor.objects.filter(profile_id=profile_id).first()

    if not tutor:
        messages.error(request, "Debes completar la información del tutor antes de gestionar estudiantes.")
        return redirect("cargar_tutor")

    estudiantes = Estudiante.objects.filter(tutor=tutor)

    return render(request, 'estudiante/listar_estudiantes.html', {"estudiantes": estudiantes})


def ver_estudiante(request):
    return render(request, 'estudiante/ver_estudiante.html')


def consultar_apto(request):
    return render(request, 'estudiante/consultar_apto.html')

@login_required
def editar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            estudiante = form.save()
            messages.success(request, "Estudiante actualizado con éxito.")
            return redirect('listar_estudiantes')  # Redirigir a la lista de estudiantes
        else:
            messages.error(request, "Error en el formulario. Verifica los datos ingresados.")
    else:
        form = EstudianteForm(instance=estudiante)  # Cargar los datos existentes en el formulario

    return render(request, 'estudiante/editar_estudiante.html', {'form': form, 'estudiante': estudiante})

@login_required
def cargar_tutor(request):
    # 📌 Obtener el perfil del estudiante desde la sesión
    profile_id = request.session.get('user_profile_id')
    profile = Profile.objects.filter(id=profile_id, rol="estudiante").first()
    
    if not profile:
        messages.error(request, "Error al cargar tutor. Intenta nuevamente.")
        return redirect('home')

    # 📌 Verificar si ya tiene un tutor
    tutor = Tutor.objects.filter(profile=profile).first()

    if tutor:
        messages.success(request, "Ya tienes un tutor registrado.")
        return redirect('menu_estudiante')

    if request.method == 'POST':
        form = TutorForm(request.POST)
        if form.is_valid():
            tutor = form.save(commit=False)
            tutor.profile = profile  # Asociar el tutor al perfil del estudiante
            tutor.save()
            messages.success(request, "Tutor registrado con éxito.")
            return redirect('menu_estudiante')  # ✅ Redirigir a menu_estudiante
        else:
            messages.error(request, "Error en el formulario. Revisa los datos.")
    else:
        form = TutorForm()

    return render(request, 'estudiante/cargar_tutor.html', {'form': form, 'profile': profile})

@login_required
def eliminar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    if request.method == "POST":
        estudiante.delete()
        messages.success(request, "Estudiante eliminado con éxito.")
        return redirect('listar_estudiantes')  # Redirigir a la lista de estudiantes

    return render(request, 'estudiante/eliminar_estudiante.html', {'estudiante': estudiante})




@login_required
def datos_personales(request):
    profile = Profile.objects.filter(user=request.user).first()  # Obtener el perfil del usuario autenticado

    if not profile:
        return render(request, "error.html", {"mensaje": "No tienes un perfil asociado."})

    tutor = Tutor.objects.filter(profile=profile).first()  # Buscar tutor asociado

    context = {
        "profile": profile,
        "tutor": tutor,
    }
    return render(request, "estudiante/datos_personales.html", context)

@login_required
def seleccionar_estudiante(request):
    # Obtener los estudiantes que no tienen antecedentes registrados
    estudiantes_sin_antecedentes = Estudiante.objects.filter(antecedentes__isnull=True)


    context = {
        'estudiantes_sin_antecedentes': estudiantes_sin_antecedentes
    }

    return render(request, 'estudiante/cargar_antecedentes.html', context)
@login_required
def cargar_antecedente_estudiante(request):
    estudiante_id = request.GET.get('estudiante_id')
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    if request.method == "POST":
        form = AntecedentesCUSForm(request.POST)
        if form.is_valid():
            antecedente = form.save(commit=False)
            antecedente.estudiante = estudiante  # Asociar el estudiante al antecedente
            antecedente.save()
            return redirect('menu_estudiante')  # Redirigir a la página principal del estudiante
    else:
        form = AntecedentesCUSForm()

    return render(request, 'estudiante/cargar_antecedente_form.html', {'form': form, 'estudiante': estudiante})

@login_required
def ver_antecedentes(request):
    # Obtener estudiantes que tienen antecedentes cargados
    estudiantes_con_antecedentes = Estudiante.objects.filter(antecedentes__isnull=False)

    context = {
        'estudiantes_con_antecedentes': estudiantes_con_antecedentes
    }
    return render(request, 'estudiante/ver_antecedentes.html', context)

@login_required
def detalle_antecedente(request, estudiante_id):
    # Obtener el estudiante y su antecedente asociado
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    antecedente = get_object_or_404(AntecedentesCUS, estudiante=estudiante)

    context = {
        'estudiante': estudiante,
        'antecedente': antecedente
    }
    return render(request, 'estudiante/detalle_antecedente.html', context)