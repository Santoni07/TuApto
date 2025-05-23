
from django.contrib import admin
from django.urls import path
from django.conf import settings

from core import views
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('info_prest', views.info_prest, name='info_prest'),
    path('account/', include('account.urls')),
    path('persona/', include('persona.urls')),
 
    path('registro-medico/', include('RegistroMedico.urls')), 
    path('medico/', include('Medico.urls')),
    path('Representate/', include('Representate.urls')),
    path('InfoNovedades/', include('InfoNovedades.urls')),
    path('estudiante/', include('estudiante.urls')),
    path('cus/', include('Cus.urls'))
    
   
    
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)