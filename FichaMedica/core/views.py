from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from publicidad.models import Publicidad



def home(request):
    publicidades = Publicidad.objects.all()

    if request.method == 'POST':
        tipo = request.POST.get("tipo_formulario")

        # ------------------------------
        # FORMULARIO "Quiero ser Prestador"
        # ------------------------------
        if tipo == "quiero_prestador":
            nombre = request.POST.get("name")
            email = request.POST.get("email")
            mensaje = request.POST.get("message")

            cuerpo = f"""
            Consulta desde formulario "Quiero ser prestador":
            Nombre: {nombre}
            Email: {email}
            Mensaje:
            {mensaje}
            """

            send_mail(
                subject='Consulta - Quiero ser prestador',
                message=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['aasantoni888@hotmail.com'],
            )

            messages.success(request, '✅ Consulta enviada correctamente.')
            return HttpResponseRedirect(reverse('home') + '#quiero-ser-prestador') 

        # ------------------------------
        # FORMULARIO DEL FOOTER
        # ------------------------------
        elif tipo == "footer_contacto":
            nombre = request.POST.get("nombre")
            email = request.POST.get("email")
            mensaje = request.POST.get("mensaje")

            cuerpo = f"""
            Mensaje desde formulario de pie de página:
            Nombre: {nombre}
            Email: {email}
            Mensaje:
            {mensaje}
            """

            send_mail(
                subject='Consulta desde el Footer',
                message=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['aasantoni888@hotmail.com'],
            )

            messages.success(request, '✅ Tu mensaje fue enviado correctamente desde el pie de página.')
            return HttpResponseRedirect(reverse('home') + '#footer')

    return render(request, 'core/home.html', {'publicidades': publicidades})