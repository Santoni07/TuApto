from datetime import timedelta
import os
from django.db import models
from persona.models import  Torneo ,Jugador
from Medico.models import Medico
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from django.utils.timezone import now


class AntecedenteEnfermedades(models.Model):
    jugador = models.OneToOneField(Jugador, on_delete=models.CASCADE, related_name='antecedentes')

    fue_operado = models.BooleanField(null=True, blank=True, default=None)
    toma_medicacion = models.BooleanField(null=True, blank=True, default=None)
    estuvo_internado = models.BooleanField(null=True, blank=True, default=None)
    sufre_hormigueos = models.BooleanField(null=True, blank=True, default=None)
    es_diabetico = models.BooleanField(null=True, blank=True, default=None)
    es_asmatico = models.BooleanField(null=True, blank=True, default=None)  
    es_alergico = models.BooleanField(null=True, blank=True, default=None)
    alerg_observ = models.CharField(max_length=100, null=True, blank=True, default=None)
    antecedente_epilepsia = models.BooleanField(null=True, blank=True, default=None)
    desviacion_columna = models.BooleanField(null=True, blank=True, default=None)
    dolor_cintura = models.BooleanField(null=True, blank=True, default=None)
    fracturas = models.BooleanField(null=True, blank=True, default=None)
    dolores_articulares = models.BooleanField(null=True, blank=True, default=None)
    falta_aire = models.BooleanField(null=True, blank=True, default=None)
    traumatismos_craneo = models.BooleanField(null=True, blank=True, default=None)
    dolor_pecho = models.BooleanField(null=True, blank=True, default=None)
    perdida_conocimiento = models.BooleanField(null=True, blank=True, default=None)
    presion_arterial = models.BooleanField(null=True, blank=True, default=None)
    muerte_subita_familiar = models.BooleanField(null=True, blank=True, default=None)
    enfermedad_cardiaca_familiar = models.BooleanField(null=True, blank=True, default=None)
    soplo_cardiaco = models.BooleanField(null=True, blank=True, default=None)
    abstenerse_competencia = models.BooleanField(null=True, blank=True, default=None)
    antecedentes_coronarios_familiares = models.BooleanField(null=True, blank=True, default=None)
    fumar_hipertension_diabetes = models.BooleanField(null=True, blank=True, default=None)
    fhd_observacion = models.CharField(max_length=100, null=True, blank=True, default=None)
    consumo_cocaina_anabolicos = models.BooleanField(null=True, blank=True, default=None)
    cca_observaciones = models.CharField(max_length=100, null=True, blank=True, default=None)

    class Meta:
        db_table = 'antecedente_enfermedades'

    def __str__(self):
        return f"Antecedentes de {self.jugador.persona.profile.nombre} {self.jugador.persona.profile.apellido}"

class RegistroMedico(models.Model):
    ESTADO_FICHA = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESO', 'En proceso'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('VENCIDO', 'Vencido'),  # Nuevo estado agregado
    ]
    
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='registros_medicos')
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=45, choices=ESTADO_FICHA, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_caducidad = models.DateField(blank=True, null=True)
    fecha_de_llenado = models.DateField(blank=True, null=True)
    observacion = models.CharField(max_length=200, blank=True, null=True)
    consentimiento_persona = models.BooleanField(null=True, blank=True)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'ficha_registro'

    def __str__(self):
        return f"Ficha Médica {self.id} - {self.jugador.persona.profile.nombre} {self.jugador.persona.profile.apellido} - {self.torneo.nombre}"

    @staticmethod
    def marcar_fichas_vencidas():
        """Marca como 'VENCIDO' las fichas médicas que han pasado su fecha de caducidad."""
        hoy = now().date()
        fichas_vencidas = RegistroMedico.objects.filter(fecha_caducidad__lt=hoy, estado__in=['PENDIENTE', 'PROCESO', 'APROBADA'])

        if fichas_vencidas.exists():
            fichas_vencidas.update(estado='VENCIDO')
            print(f"Se han marcado {fichas_vencidas.count()} fichas médicas como 'VENCIDO'.")

    @staticmethod
    def eliminar_fichas_vencidas():
        """Elimina fichas médicas que estén en estado 'VENCIDO'."""
        fichas_a_eliminar = RegistroMedico.objects.filter(estado='VENCIDO')

        if fichas_a_eliminar.exists():
            print(f"Eliminando {fichas_a_eliminar.count()} fichas médicas en estado 'VENCIDO'...")
            fichas_a_eliminar.delete()
    
class EstudiosMedico(models.Model):
    TIPO_ESTUDIO = [
        ('ORINA', 'Análisis de Orina'),
        ('ELECTRO', 'Electrocardiograma'),
        ('ERGOMETRIA', 'Ergometría'),
    ]
    
    idestudio = models.AutoField(primary_key=True)
    ficha_medica = models.ForeignKey(RegistroMedico, on_delete=models.CASCADE)  # Relación con la ficha médica
    tipo_estudio = models.CharField(max_length=20, choices=TIPO_ESTUDIO)  # Tipo de estudio médico
    
    archivo = models.FileField(upload_to='estudios/', null=True, blank=True)  # Archivo cargado (imágenes, PDFs, etc.)
    observaciones = models.CharField(max_length=200, null=True, blank=True)  # Observaciones adicionales
    
    class Meta:
        db_table = 'estudios_medicos'
        verbose_name = 'Estudio Médico'
        verbose_name_plural = 'Estudios Médicos'

    def __str__(self):
        return f'{self.get_tipo_estudio_display()} - {self.ficha_medica.jugador.persona.profile.nombre} {self.ficha_medica.jugador.persona.profile.apellido}'

    # Señal para eliminar el archivo al eliminar el objeto

@receiver(post_delete, sender=EstudiosMedico)
def eliminar_archivo_post_delete(sender, instance, **kwargs):
    if instance.archivo:
        if os.path.isfile(instance.archivo.path):
            os.remove(instance.archivo.path)



class ElectroBasal(models.Model):
    idelectro_basal = models.AutoField(primary_key=True)
    ritmo = models.CharField(max_length=45, null=True, blank=True)
    PQ = models.CharField(max_length=45, null=True, blank=True)
    frecuencia = models.CharField(max_length=45, null=True, blank=True)
    arritmias = models.CharField(max_length=45, null=True, blank=True)
    ejeQRS = models.CharField(max_length=45, null=True, blank=True)
    trazadoNormal = models.CharField(max_length=45, null=True, blank=True)
    observaciones = models.CharField(max_length=45, null=True, blank=True,default='Sin observaciones')
    
    # Relación con el modelo RegistroMedico, renombrada a ficha_medica
    ficha_medica = models.OneToOneField(
        RegistroMedico, 
        on_delete=models.CASCADE,
        unique=True
    )

    class Meta:
        db_table = 'electro_basal'
        verbose_name = 'Electro Basal'
        verbose_name_plural = 'Electro Basales'

    def __str__(self):
        return f"Electro Basal {self.idelectro_basal} - Ficha Médica {self.ficha_medica.idfichaMedica}"

class ElectroEsfuerzo(models.Model):
    idelectro_esfuerzo = models.AutoField(primary_key=True)
    observaciones = models.CharField(max_length=200, null=True, blank=True,default='Sin observaciones')
    
    # Relación con el modelo RegistroMedico, renombrada a ficha_medica
    ficha_medica = models.OneToOneField(
        RegistroMedico,
        on_delete=models.CASCADE,
        unique=True
    )

    class Meta:
        db_table = 'electro_esfuerzo'
        verbose_name = 'Electro Esfuerzo'
        verbose_name_plural = 'Electro Esfuerzos'

    def __str__(self):
        return f"Electro Esfuerzo {self.idelectro_esfuerzo} - Ficha Médica {self.ficha_medica.idfichaMedica}"
    
    
class Cardiovascular(models.Model):
    idcardiovascular = models.AutoField(primary_key=True)
    auscultacion = models.CharField(max_length=45, null=True, blank=True)
    soplos = models.CharField(max_length=45, null=True, blank=True)
    R1 = models.CharField(max_length=45, null=True, blank=True)
    tension_arterial = models.CharField(max_length=45, null=True, blank=True)
    R2 = models.CharField(max_length=45, null=True, blank=True)
    observaciones = models.CharField(max_length=200, null=True, blank=True,default='Sin observaciones')
    ruidos_agregados = models.CharField(max_length=45, null=True, blank=True)
    
    # Relación con el modelo RegistroMedico, renombrada a ficha_medica
    ficha_medica = models.OneToOneField(
        RegistroMedico,
        on_delete=models.CASCADE,
        unique=True
    )

    class Meta:
        db_table = 'cardiovascular'
        verbose_name = 'Examen Cardiovascular'
        verbose_name_plural = 'Exámenes Cardiovasculares'

    def __str__(self):
        return f"Cardiovascular {self.idcardiovascular} - Ficha Médica {self.ficha_medica.idfichaMedica}"
    
class Laboratorio(models.Model):
    idlaboratorio = models.AutoField(primary_key=True)
    citologico = models.CharField(max_length=45, null=True, blank=True,default='S/D')
    orina = models.CharField(max_length=45, null=True, blank=True,default='S/D')
    colesterol = models.CharField(max_length=45, null=True, blank=True,default='S/D')
    uremia = models.CharField(max_length=45, null=True, blank=True,default='S/D')
    glucemia = models.CharField(max_length=45, null=True, blank=True,default='S/D')
    otros = models.CharField(max_length=45, null=True, blank=True,default='S/D')
    
    # Relación con el modelo RegistroMedico, renombrada a ficha_medica
    ficha_medica = models.OneToOneField(
        RegistroMedico,
        on_delete=models.CASCADE,
        unique=True
    )

    class Meta:
        db_table = 'laboratorio'
        verbose_name = 'Examen de Laboratorio'
        verbose_name_plural = 'Exámenes de Laboratorio'

    def __str__(self):
        return f"Laboratorio {self.idlaboratorio} - Ficha Médica {self.ficha_medica.idfichaMedica}"
    
class Torax(models.Model):
    idtorax = models.AutoField(primary_key=True)
    observaciones = models.CharField(max_length=200, null=True, blank=True,default='Sin observaciones')
    
    # Relación con el modelo RegistroMedico, renombrada a ficha_medica
    ficha_medica = models.OneToOneField(
        RegistroMedico,
        on_delete=models.CASCADE,
        unique=True
    )

    class Meta:
        db_table = 'torax'
        verbose_name = 'Examen de Tórax'
        verbose_name_plural = 'Exámenes de Tórax'

    def __str__(self):
        return f"Tórax {self.idtorax} - Ficha Médica {self.ficha_medica.idfichaMedica}"
    

class Oftalmologico(models.Model):
    idoftalmologico = models.AutoField(primary_key=True)
    od = models.CharField(max_length=45, null=True, blank=True)  # Ojo derecho
    oi = models.CharField(max_length=45, null=True, blank=True)  # Ojo izquierdo

    # Relación con el modelo RegistroMedico, renombrada a ficha_medica
    ficha_medica = models.OneToOneField(
        RegistroMedico,
        on_delete=models.CASCADE,
        unique=True
    )

    class Meta:
        db_table = 'oftalmologico'
        verbose_name = 'Examen Oftalmológico'
        verbose_name_plural = 'Exámenes Oftalmológicos'

    def __str__(self):
        return f"Oftalmológico {self.idoftalmologico} - Ficha Médica {self.ficha_medica.idfichaMedica}"
    

class OtrosExamenesClinicos(models.Model):
    ficha_medica = models.OneToOneField(RegistroMedico, on_delete=models.CASCADE, related_name='otros_examenes')
    respiratorio_observaciones = models.CharField(max_length=200, null=True, blank=True,default='Sin observaciones')
    renal_observaciones = models.CharField(max_length=200, null=True, blank=True,default='Sin observaciones')
    digestivo_observaciones = models.CharField(max_length=200, null=True, blank=True,default='Sin observaciones')
    osteoarticular_observaciones = models.CharField(max_length=200, null=True, blank=True,default='Sin observaciones')

    def __str__(self):
        return f"Otros Exámenes Clínicos de {self.ficha_medica}"
    
    
class EliminacionFichaMedica(models.Model):
    jugador = models.CharField(max_length=255)  # Nombre del jugador
    medico = models.CharField(max_length=255)  # Nombre del médico que eliminó la ficha
    fecha_eliminacion = models.DateTimeField(default=now)  # Fecha de eliminación

    def __str__(self):
        return f"Ficha eliminada de {self.jugador} por {self.medico} el {self.fecha_eliminacion.strftime('%d-%m-%Y %H:%M')}"