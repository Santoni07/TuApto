from datetime import date
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import AntecedentesCUS, Estudiante, EstudianteColegio, Tutor, Colegio
from .forms import AntecedentesCUSForm, EstudianteForm, TutorForm
from account.models import Profile
from django.contrib.auth.decorators import login_required
from Cus.models import Cus
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from Cus.models import *
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
    tutor = Tutor.objects.filter(profile=profile).first()

    if not tutor:
        messages.warning(request, "Debes completar la información del tutor antes de continuar.")
        return redirect('cargar_tutor')  # ❌ Si no tiene tutor, redirigir a cargar tutor

    # 🔔 Obtener estudiantes a cargo del tutor
    estudiantes = Estudiante.objects.filter(tutor=tutor)

    # ✅ Obtener CUS con estado APROBADO
    notificaciones_cus = Cus.objects.filter(estudiante__in=estudiantes, estado="APROBADA")

    return render(request, 'estudiante/menu_estudiante.html', {
        "notificaciones_cus": notificaciones_cus,
        "profile": profile,
        "tutor": tutor
    })
@login_required
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
@login_required
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

@login_required
def ver_estudiante(request):
    return render(request, 'estudiante/ver_estudiante.html')
@login_required
def consultar_apto(request):
    estudiantes = Estudiante.objects.filter(cus__isnull=False).distinct()

    perfil = None
    profile_id = request.session.get("user_profile_id")
    if profile_id:
        try:
            perfil = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            perfil = None

    return render(request, 'estudiante/consultar_apto.html', {
        'estudiantes': estudiantes,
        'perfil': perfil,
    })

@login_required
def editar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    # Traer el colegio activo actual si existe
    relacion_actual = EstudianteColegio.objects.filter(estudiante=estudiante, activo=True).first()

    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        colegio_id = request.POST.get("colegio")

        if form.is_valid():
            estudiante = form.save()

            # Si el colegio cambió, actualizar la relación
            if colegio_id and (not relacion_actual or int(colegio_id) != relacion_actual.colegio.id):
                # Desactivar el actual si existe
                if relacion_actual:
                    relacion_actual.activo = False
                    relacion_actual.save()

                # Activar el nuevo
                nuevo_colegio = Colegio.objects.get(id=colegio_id)
                EstudianteColegio.objects.create(estudiante=estudiante, colegio=nuevo_colegio, activo=True)

            messages.success(request, "Estudiante actualizado con éxito.")
            return redirect('listar_estudiantes')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos ingresados.")
    else:
        form = EstudianteForm(instance=estudiante)

    colegios = Colegio.objects.all()

    return render(request, 'estudiante/editar_estudiante.html', {
        'form': form,
        'estudiante': estudiante,
        'colegios': colegios,
        'colegio_actual': relacion_actual.colegio if relacion_actual else None
    })

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
    profile = Profile.objects.filter(user=request.user).first()
    
    if not profile:
        return render(request, "error.html", {"mensaje": "No tienes un perfil asociado."})

    tutor = Tutor.objects.filter(profile=profile).first()

    estudiantes = Estudiante.objects.filter(tutor=tutor) if tutor else []

    # Añadir el colegio a cada estudiante
    for est in estudiantes:
        relacion = EstudianteColegio.objects.filter(estudiante=est, activo=True).select_related('colegio').first()
        est.colegio = relacion.colegio if relacion else None

    context = {
        "profile": profile,
        "tutor": tutor,
        "estudiantes": estudiantes,
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
            antecedente.estudiante = estudiante
            antecedente.save()

            # 🆕 Crear automáticamente un CUS asociado
            Cus.objects.create(
                estudiante=estudiante,
                estado='PROCESO',
                fecha_creacion=now(),
                consentimiento_persona=True
            )

             # ✅ Mensaje para mostrar modal
            messages.success(request, "Antecedentes guardados con éxito.")

            # Volvemos al mismo form para activar el modal
            return redirect(request.path + f"?estudiante_id={estudiante.id}")
    else:
        form = AntecedentesCUSForm()

    return render(request, 'estudiante/cargar_antecedente_form.html', {
        'form': form,
        'estudiante': estudiante
    })
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



 
@login_required
def lista_estudiantes_para_cus(request):
    # Obtener todos los estudiantes del tutor logueado
    profile_id = request.session.get("user_profile_id")
    estudiantes = Estudiante.objects.filter(tutor__profile__id=profile_id)
    
    context = {
        'estudiantes': estudiantes,
    }
    return render(request, 'estudiante/lista_generar_cus.html', context)

@login_required
def generar_cus_para_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    # Crear nuevo CUS
    nuevo_cus = Cus.objects.create(
        estudiante=estudiante,
        fecha_de_llenado=date.today(),
        estado="INCOMPLETO"
    )

    messages.success(request, f"✅ Se ha creado el CUS para {estudiante.nombre} {estudiante.apellido}")
    return redirect('cus_update_view', cus_id=nuevo_cus.id)

@login_required
@csrf_exempt
def generar_cus_ajax(request, estudiante_id):
    if request.method == "POST":
        estudiante = get_object_or_404(Estudiante, id=estudiante_id)

        if Cus.objects.filter(estudiante=estudiante, estado__in=["EN PROCESO", "APROBADA"]).exists():
            return JsonResponse({"success": False, "message": "El estudiante ya tiene un CUS activo."}, status=400)

        nuevo_cus = Cus.objects.create(estudiante=estudiante, estado="PROCESO")

        return JsonResponse({
            "success": True,
            "cus_id": nuevo_cus.id
        })

    return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)

# DATOS PARA LA CURVA DE CRECIMIENTO 
@login_required
def curva_crecimiento_view(request):
    estudiantes = Estudiante.objects.all()
    datos = []

    estudiante_id = request.GET.get('estudiante_id')
    estudiante_seleccionado = None

    if estudiante_id:
        estudiante_seleccionado = get_object_or_404(Estudiante, id=estudiante_id)

        registros = []

        # CUS original
        cus = Cus.objects.filter(estudiante=estudiante_seleccionado).order_by('fecha_de_llenado').first()
        if cus and hasattr(cus, 'examen_fisico'):
            peso = float(cus.examen_fisico.peso or 0)
            talla = float(cus.examen_fisico.talla or 0)
            imc = round(peso / ((talla/100)**2), 2) if peso and talla else 0
            registros.append({
                'fecha': cus.fecha_de_llenado.strftime('%Y-%m-%d') if cus.fecha_de_llenado else 'CUS',
                'peso': peso,
                'talla': talla,
                'imc': imc
            })

        # Actualizaciones
        actualizaciones = ActualizacionCUS.objects.filter(cus__estudiante=estudiante_seleccionado).order_by('fecha')
        for act in actualizaciones:
            peso = float(act.peso or 0)
            talla = float(act.talla or 0)
            imc = round(peso / ((talla/100)**2), 2) if peso and talla else 0
            registros.append({
                'fecha': act.fecha.strftime('%Y-%m-%d'),
                'peso': peso,
                'talla': talla,
                'imc': imc
            })

        datos = json.dumps(registros)
        print(F'Datos del estudiante ',datos)

    context = {
        'estudiantes': estudiantes,
        'estudiante_seleccionado': estudiante_seleccionado,
        'datos': datos
    }
    return render(request, 'estudiante/curva_crecimiento.html', context)