
from django.urls import path
from . import views


urlpatterns = [
   path('menu_estudiante/', views.home_estudiante, name='menu_estudiante'),
   path('cargar_estudiante/', views.cargar_estudiante, name='cargar_estudiante'),
   path('cargar_tutor/', views.cargar_tutor, name='cargar_tutor'),
   path('datos_personales/', views.datos_personales, name='datos_personales'),
   path('editar_estudiante/<int:estudiante_id>/', views.editar_estudiante, name='editar_estudiante'),
   path('eliminar_estudiante/<int:estudiante_id>/', views.eliminar_estudiante, name='eliminar_estudiante'),
   path('listar_estudiantes/', views.listar_estudiantes, name='listar_estudiantes'),
   path('ver_estudiante/', views.ver_estudiante, name='ver_estudiante'),
   path('ver-antecedentes/', views.ver_antecedentes, name='ver_antecedentes'),
   path('detalle-antecedente/<int:estudiante_id>/', views.detalle_antecedente, name='detalle_antecedente'),
   path('antecedente/actualizar/<int:estudiante_id>/', views.actualizar_antecedente_si_cus_vencido, name='actualizar_antecedente_si_cus_vencido'),

   path('consultar_apto/', views.consultar_apto, name='consultar_apto'),
   path('seleccionar_estudiante/', views.seleccionar_estudiante, name='seleccionar_estudiante'),
   path('cargar_antecedente/', views.cargar_antecedente_estudiante, name='cargar_antecedente_estudiante'),
   path('estudiante/generar_cus/', views.lista_estudiantes_para_cus, name='lista_estudiantes_para_cus'),
   path('ajax/generar_cus/<int:estudiante_id>/', views.generar_cus_ajax, name='generar_cus_ajax'),
   path('curva_crecimiento/', views.curva_crecimiento_view, name='curva_crecimiento'),


    
]
