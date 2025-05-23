

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, QueryDict
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Representante, RepresenteColegio
from RegistroMedico.models import RegistroMedico, EstudiosMedico
from persona.models import Categoria,Equipo,JugadorCategoriaEquipo,CategoriaEquipo,Jugador
from django.db.models import Q
from django.shortcuts import get_object_or_404
from estudiante.models import Estudiante
from account.models import Profile
from datetime import datetime, date


class RepresentanteHomeView(LoginRequiredMixin, View):
    def get(self, request):
        profile_id = request.session.get("user_profile_id")
        profile = get_object_or_404(Profile, id=profile_id)

        representante = Representante.objects.filter(profile=profile).first()
        if not representante:
            return render(request, 'Representante/torneo_home.html', {
                "error": "No se encontró información del representante."
            })

        categorias = Categoria.objects.filter(torneo=representante.torneo)
        equipos = Equipo.objects.filter(categoria_equipos__categoria__in=categorias).distinct()

        # Filtros y búsqueda
        query_dict = QueryDict(mutable=True)
        query_dict.update(request.GET)

        filter_type = query_dict.get('filter_type', None)
        filter_team_list = query_dict.getlist('filter_team')  # Obtén todos los valores para filter_team
        filter_team = filter_team_list[0] if filter_team_list else None  # Usa solo el primero si hay duplicados
        filter_category = query_dict.get('filter_category', None)
        search_query = query_dict.get('search_query', None)

        print("Parámetros recibidos:", query_dict)
        jugadores = []  # Asegúrate de que se limpie al comienzo

        try:
            if filter_type == 'equipo' :
                jugadores = []  # Limpia antes de ejecutar el filtro
                equipo_id = int(filter_team)
                print("Equipo ID:", equipo_id)
               
                jugadores = Jugador.objects.filter(
                        jugadorcategoriaequipo__categoria_equipo__equipo_id=equipo_id,
                        jugadorcategoriaequipo__categoria_equipo__categoria__torneo=representante.torneo
                    ).distinct()
                print("Jugadores obtenidos:", jugadores)

            elif filter_type == 'categoria' and filter_category:
                print("Categoría recibida:", filter_category)
                jugadores = []  # Limpia antes de ejecutar el filtro
                categoria_id = int(filter_category)
                print("Categoría ID:", categoria_id)
                categoria = get_object_or_404(Categoria, id=categoria_id)
                print("Categoría encontrada:", categoria)

                equipos = Equipo.objects.filter(categoria_equipos__categoria=categoria).distinct()
                print("Equipos filtrados por categoría:", equipos)

                if filter_team:
                    equipo_id = int(filter_team)
                    print("Equipo ID:", equipo_id)
                    jugadores = Jugador.objects.filter(
                        jugadorcategoriaequipo__categoria_equipo__equipo_id=equipo_id,
                        jugadorcategoriaequipo__categoria_equipo__categoria_id=categoria_id,
                        jugadorcategoriaequipo__categoria_equipo__categoria__torneo=representante.torneo
                    ).distinct()
                

            elif filter_type == 'persona' and search_query:
                jugadores = []  # Limpia antes de ejecutar el filtro
                jugadores = Jugador.objects.filter(
                    Q(persona__profile__dni__icontains=search_query) |
                    Q(persona__profile__nombre__icontains=search_query) |
                    Q(persona__profile__apellido__icontains=search_query),
                    jugadorcategoriaequipo__categoria_equipo__categoria__torneo=representante.torneo
                ).distinct()

        except ValueError as e:
            print("Error procesando los filtros:", e)
        except Categoria.DoesNotExist:
            print("Categoría no válida o no encontrada.")
        except Equipo.DoesNotExist:
            print("Equipo no válido o no encontrado.")

        # Filtrar jugadores con registro médico aprobado y añadir estudios médicos
        jugadores_info = []
        for jugador in jugadores:
            registro_medico = RegistroMedico.objects.filter(jugador=jugador, torneo=representante.torneo).first()
            if registro_medico:
                estudios_medicos = EstudiosMedico.objects.filter(jugador=registro_medico.jugador)
                jugador_info = {
                    "apellido": jugador.persona.profile.apellido,
                    "nombre": jugador.persona.profile.nombre,
                    "dni": jugador.persona.profile.dni,
                    "id": jugador.id,
                    "registro_id": registro_medico.id,
                    "registro_medico_estado": registro_medico.estado,
                    "estudios_medicos": [
                        {
                            'tipo': estudio.get_tipo_estudio_display(),
                            'archivo': estudio.archivo.url if estudio.archivo else None,
                            'observaciones': estudio.observaciones
                        }
                        for estudio in EstudiosMedico.objects.filter(
                            jugador=jugador,
                            fecha_caducidad__gte=date.today()  
                        )
                    ],
                }

                jugador_info['categorias_equipo'] = [
                    {
                        'nombre_categoria': jce.categoria_equipo.categoria.nombre,
                        'nombre_equipo': jce.categoria_equipo.equipo.nombre,
                        'torneo': jce.categoria_equipo.categoria.torneo.nombre
                    }
                    for jce in jugador.jugadorcategoriaequipo_set.all()
                    if jce.categoria_equipo.categoria.torneo == representante.torneo
                ]
                jugadores_info.append(jugador_info)
    
        context = {
            "representante": representante,
            "jugadores_info": jugadores_info,
            "equipos": equipos,
            "categorias": categorias,
        }
        print("Jugadores info:", jugadores_info)
        return render(request, 'Representante/torneo_home.html', context)  
    
class TraerEquiposPorCategorias(LoginRequiredMixin, View):
    def get(self, request):
        category_id = request.GET.get('category_id')
        if category_id:
            try:
                categoria = get_object_or_404(Categoria, id=category_id)
                equipos = Equipo.objects.filter(categoria_equipos__categoria=categoria).values('id', 'nombre').distinct()
                return JsonResponse({'equipos': list(equipos)})
            except Categoria.DoesNotExist:
                return JsonResponse({'error': 'Categoría no encontrada.'}, status=404)
        return JsonResponse({'error': 'ID de categoría no proporcionado.'}, status=400)


 

def obtener_jugadores_por_equipo(equipo_id, torneo_id):
    return Jugador.objects.filter(
        jugadorcategoriaequipo__categoria_equipo__equipo_id=equipo_id,
        jugadorcategoriaequipo__categoria_equipo__categoria__torneo_id=torneo_id
    ).distinct()
def obtener_equipos_por_categoria(categoria_id):
    # Obtener la categoría seleccionada
    categoria = get_object_or_404(Categoria, id=categoria_id)

    # Filtrar las relaciones de CategoriaEquipo asociadas a la categoría
    categorias_equipos = CategoriaEquipo.objects.filter(categoria=categoria)

    # Obtener los equipos únicos asociados a la categoría
    equipos = [ce.equipo for ce in categorias_equipos]
    equipos = list(set(equipos))
    print(equipos)

    return equipos
 
def obtener_jugadores_por_torneo(torneo_id):
    # Obtener todos los jugadores del torneo
    jugadores_categoria_equipos = JugadorCategoriaEquipo.objects.filter(
        categoria_equipo__categoria__torneo_id=torneo_id
    ).distinct()
    
    return [jce.jugador for jce in jugadores_categoria_equipos] 

    
def traer_equipos(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria_id')
        if categoria_id:
            categoria = Categoria.objects.get(id=categoria_id)
            equipos = Equipo.objects.filter(categoria_equipos__categoria=categoria).values('id', 'nombre')
            return JsonResponse({'equipos': list(equipos)})
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


@login_required
def colegio_home_view(request):
    profile_id = request.session.get("user_profile_id")
    representante = get_object_or_404(RepresenteColegio, Profile_id=profile_id)
    colegio = representante.colegio

    buscar = request.GET.get("buscar")
    dni = request.GET.get("dni")
    estado = request.GET.get("estado")
    anio = request.GET.get("anio")
    tipo = request.GET.get("tipo")  # ✅ nuevo parámetro

    estudiantes = Estudiante.objects.none()

    # Si se selecciona tipo alumno sin más filtros, traemos todos
    if tipo == "alumno" and not buscar and not dni and not estado and not anio:
        estudiantes = Estudiante.objects.filter(
            estudiantecolegio__colegio=colegio,
            estudiantecolegio__activo=True
        ).distinct()
    elif tipo == "alumno" or buscar or dni or estado or anio:
        estudiantes = Estudiante.objects.filter(
            estudiantecolegio__colegio=colegio,
            estudiantecolegio__activo=True
        ).distinct()

        if buscar:
            estudiantes = estudiantes.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido__icontains=buscar)
            )

        if dni:
            estudiantes = estudiantes.filter(dni__icontains=dni)

        if estado:
            estudiantes = estudiantes.filter(cus__estado=estado).distinct()

        if anio:
            estudiantes = estudiantes.filter(cus__fecha_de_llenado__year=anio).distinct()

    total_alumnos = None
    total_aprobados = None

    if tipo == "alumno":
        total_alumnos = Estudiante.objects.filter(
            estudiantecolegio__colegio=colegio,
            estudiantecolegio__activo=True
        ).distinct().count()

        total_aprobados = Estudiante.objects.filter(
            estudiantecolegio__colegio=colegio,
            estudiantecolegio__activo=True,
            cus__estado="APROBADA"
        ).distinct().count()

    current_year = datetime.now().year
    anios = list(range(current_year, current_year - 6, -1))

    return render(request, "representante/colegio_home.html", {
        "colegio": colegio,
        "estudiantes": estudiantes,
        "anios": anios,
        "tipo": tipo,  # 🔁 mantener valor en el select del template
        "total_alumnos": total_alumnos,
        "total_aprobados": total_aprobados,
    })
