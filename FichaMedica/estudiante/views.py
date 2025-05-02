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
    perfil = None
    profile_id = request.session.get("user_profile_id")

    if profile_id:
        perfil = get_object_or_404(Profile, id=profile_id)

    estudiantes = Estudiante.objects.filter(
        tutor__profile=perfil,  # 🔹 Solo los estudiantes del tutor actual
        cus__isnull=False
    ).distinct()

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

            # Redirigimos para reiniciar el formulario y mostrar el modal
            return redirect(request.path + f"?estudiante_id={estudiante.id}")
    else:
        form = AntecedentesCUSForm()

    return render(request, 'estudiante/cargar_antecedente_form.html', {
        'form': form,
        'estudiante': estudiante,
        'actualizar': False  # 👈 aclaramos que es carga nueva
    })
@login_required
def ver_antecedentes(request):
    profile = Profile.objects.filter(user=request.user, rol='estudiante').first()

    if not profile:
        messages.error(request, "No se encontró un perfil de estudiante asociado a tu cuenta.")
        return redirect('home')  # O donde quieras redirigir

    tutor = Tutor.objects.get(profile=profile)
    estudiantes = Estudiante.objects.filter(
        tutor=tutor,
        antecedentes__isnull=False
    ).distinct()
    

    datos_estudiantes = []

    for estudiante in estudiantes:
        ultimo_antecedente = estudiante.antecedentes.order_by('-id').first()
        cus = Cus.objects.filter(estudiante=estudiante).order_by('-id').first()
        estado_cus = cus.estado if cus else None
        fecha_caducidad_cus = cus.fecha_caducidad if cus else None

        actualizacion = ActualizacionCUS.objects.filter(cus=cus).order_by('-fecha').first()

        datos_estudiantes.append({
            'estudiante': estudiante,
            'cus': cus,
            'estado_cus': estado_cus,
            'fecha_caducidad': fecha_caducidad_cus,
            'tiene_actualizacion': bool(actualizacion),
            'vencimiento': actualizacion.vencimiento if actualizacion else None,
            'puede_editar': estado_cus == 'VENCIDO',
            'antecedente': ultimo_antecedente
        })

    context = {
        'datos_estudiantes': datos_estudiantes
    }
    return render(request, 'estudiante/ver_antecedentes.html', context)



@login_required
def detalle_antecedente(request, estudiante_id):
    # Buscamos el perfil del usuario con rol 'estudiante' (que en tu caso representa al tutor)
    profile = Profile.objects.filter(user=request.user, rol='estudiante').first()

    if not profile:
        messages.error(request, "No se encontró un perfil de estudiante asociado a tu cuenta.")
        return redirect('home')

    tutor = Tutor.objects.get(profile=profile)

    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    # Validamos que el estudiante pertenezca al tutor logueado
    if estudiante.tutor != tutor:
        messages.error(request, "No tienes permiso para ver este antecedente.")
        return redirect('ver_antecedentes')

    antecedente = AntecedentesCUS.objects.filter(estudiante=estudiante).order_by('-id').first()
    print(f"Antecedente encontrado para el estudiante {estudiante.id}: {antecedente}")

    if not antecedente:
        messages.error(request, "No se encontraron antecedentes para este estudiante.")
        return redirect('ver_antecedentes')

    context = {
        'estudiante': estudiante,
        'antecedente': antecedente
    }
    return render(request, 'estudiante/detalle_antecedente.html', context)

@login_required
def lista_estudiantes_para_cus(request):
    profile_id = request.session.get("user_profile_id")
    estudiantes = Estudiante.objects.filter(tutor__profile__id=profile_id)

    estudiantes_info = []
    alguno_puede_generar = False

    for estudiante in estudiantes:
        cus = Cus.objects.filter(estudiante=estudiante).order_by('-id').first()
        puede_generar_cus = False

        if not cus:
            puede_generar_cus = True
        elif cus.estado == 'VENCIDO':
            puede_generar_cus = True
        elif cus.actualizaciones_cargadas() >= 5:
            puede_generar_cus = True

        if puede_generar_cus:
            alguno_puede_generar = True  # ✅ Si hay uno que puede, ya sabemos

        estudiantes_info.append({
            'estudiante': estudiante,
            'cus': cus,
            'puede_generar_cus': puede_generar_cus,
        })

    context = {
        'estudiantes_info': estudiantes_info,
        'alguno_puede_generar': alguno_puede_generar,  # 👈 pasamos esto
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
    profile = get_object_or_404(Profile, user=request.user, rol='estudiante')  
    tutor = get_object_or_404(Tutor, profile=profile)
    print(f'👤 Tutor: {tutor}')
    estudiantes = Estudiante.objects.filter(tutor=tutor)  # 👈 filtrar los estudiantes de ese tutor
    datos = []

    estudiante_id = request.GET.get('estudiante_id')
    estudiante_seleccionado = None

    if estudiante_id:
        estudiante_seleccionado = get_object_or_404(Estudiante, id=estudiante_id, tutor=tutor)  # 👈 además, asegurarte que sea de *su* tutor

        registros = []

        # ✅ TODOS los CUS del estudiante
        cus_qs = Cus.objects.filter(estudiante=estudiante_seleccionado).order_by('fecha_de_llenado')
        for cus in cus_qs:
            examen = ExamenFisico.objects.filter(cus=cus).first()
            if examen:
                peso = float(examen.peso or 0)
                talla = float(examen.talla or 0)
                imc = round(peso / ((talla / 100) ** 2), 2) if peso and talla else 0
                registros.append({
                    'fecha': cus.fecha_de_llenado.strftime('%Y-%m-%d') if cus.fecha_de_llenado else f'CUS #{cus.id}',
                    'peso': peso,
                    'talla': talla,
                    'imc': imc
                })

        # ✅ Actualizaciones
        actualizaciones = ActualizacionCUS.objects.filter(cus__estudiante=estudiante_seleccionado).order_by('fecha')
        for act in actualizaciones:
            peso = float(act.peso or 0)
            talla = float(act.talla or 0)
            imc = round(peso / ((talla / 100) ** 2), 2) if peso and talla else 0
            registros.append({
                'fecha': act.fecha.strftime('%Y-%m-%d'),
                'peso': peso,
                'talla': talla,
                'imc': imc
            })

        registros.sort(key=lambda x: x['fecha'])
        datos = json.dumps(registros)
        print(f'📈 Datos del estudiante {estudiante_seleccionado.id}:', datos)

    context = {
        'estudiantes': estudiantes,
        'estudiante_seleccionado': estudiante_seleccionado,
        'datos': datos
    }
    return render(request, 'estudiante/curva_crecimiento.html', context)
# Funcion para generar un nuevo antecedente si cus es vencido 
@login_required
def actualizar_antecedente_si_cus_vencido(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    # Obtener el último CUS
    ultimo_cus = Cus.objects.filter(estudiante=estudiante).order_by('-fecha_de_llenado').first()

    if not ultimo_cus or ultimo_cus.estado != 'VENCIDO':
        messages.error(request, "⚠️ No se puede actualizar. El CUS no está vencido.")
        return redirect('ver_antecedentes')

    print(f'📝 Post: {request.POST}')

    if request.method == 'POST':
        form = AntecedentesCUSForm(request.POST)
        if form.is_valid():
            nuevo = form.save(commit=False)
            nuevo.estudiante = estudiante
            nuevo.save()
            messages.success(request, "✅ Antecedente actualizado con historial guardado.")
            return redirect('ver_antecedentes')
        else:
            print("❌ Formulario no válido")
            print(form.errors)
    else:
        # precargar con los últimos antecedentes (si existen)
        antecedentes_previos = estudiante.antecedentes.order_by('-id').first()
        form = AntecedentesCUSForm(instance=antecedentes_previos)

    return render(request, 'estudiante/cargar_antecedente_form.html', {
        'form': form,
        'estudiante': estudiante,
        'cus': ultimo_cus
    })
