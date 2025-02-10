from django.core.management.base import BaseCommand
from django.utils.timezone import now
from RegistroMedico.models import RegistroMedico
from datetime import timedelta

class Command(BaseCommand):
    help = "Elimina automáticamente las fichas médicas vencidas después de 365 días"

    def handle(self, *args, **kwargs):
        hoy = now().date()
        fecha_limite = hoy - timedelta(days=365)  # Fecha de caducidad + 365 días

        fichas_a_eliminar = RegistroMedico.objects.filter(fecha_caducidad__lt=fecha_limite)

        if fichas_a_eliminar.exists():
            cantidad = fichas_a_eliminar.count()
            fichas_a_eliminar.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ {cantidad} fichas médicas eliminadas tras 365 días de vencimiento."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ No hay fichas médicas vencidas hace más de 365 días para eliminar."))