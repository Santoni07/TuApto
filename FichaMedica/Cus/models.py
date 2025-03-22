from django.db import models
from django.utils.timezone import now
from estudiante.models import Estudiante
from Medico.models import Medico
from datetime import datetime, timedelta


class Cus(models.Model):
    ESTADO_CUS = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESO', 'En proceso'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('VENCIDO', 'Vencido'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='cus')
    estado = models.CharField(max_length=45, choices=ESTADO_CUS, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_caducidad = models.DateField(blank=True, null=True)
    fecha_de_llenado = models.DateField(blank=True, null=True)
    observacion = models.CharField(max_length=200, blank=True, null=True)
    consentimiento_persona = models.BooleanField(null=True, blank=True)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'cus_ficha_medica'

    def __str__(self):
        return f"CUS {self.id} - {self.estudiante.nombre} {self.estudiante.apellido}"

    @staticmethod
    def marcar_cus_vencidas():
        """Marca como 'VENCIDO' las CUS que han pasado su fecha de caducidad."""
        hoy = now().date()
        vencidas = Cus.objects.filter(fecha_caducidad__lt=hoy, estado__in=['PENDIENTE', 'PROCESO', 'APROBADA'])

        if vencidas.exists():
            vencidas.update(estado='VENCIDO')
            print(f"Se han marcado {vencidas.count()} CUS como 'VENCIDO'.")

    @staticmethod
    def eliminar_cus_vencidas():
        """Elimina CUS que estén en estado 'VENCIDO'."""
        a_eliminar = Cus.objects.filter(estado='VENCIDO')

        if a_eliminar.exists():
            print(f"Eliminando {a_eliminar.count()} CUS en estado 'VENCIDO'...")
            a_eliminar.delete()

def default_fecha_caducidad():
    return datetime.now().date() + timedelta(days=304)



# MODELO DE EXAMEN FISICO
class ExamenFisico(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='examen_fisico')

    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Peso en kilogramos")
    talla = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Talla en centímetros")
    imc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Índice de masa corporal")
    diagnostico_antropometrico = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'examen_fisico'
        verbose_name = 'Examen Físico'
        verbose_name_plural = 'Exámenes Físicos'

    def __str__(self):
        return f"Examen Físico - CUS {self.cus.id}"

    def save(self, *args, **kwargs):
        if self.peso and self.talla:
            try:
                altura_metros = float(self.talla) / 100  # Convertir cm a metros
                self.imc = round(float(self.peso) / (altura_metros ** 2), 2)
            except (ZeroDivisionError, ValueError):
                self.imc = None  # Evita errores si talla es 0 o inválida
        else:
            self.imc = None  # No calcular si falta algún dato
        super().save(*args, **kwargs)
        
          
#MODELO DE ALIMENTACION-NUTRICION

class AlimentacionNutricion(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='alimentacion')

    solicita_plan_especial = models.BooleanField(null=True, blank=True)
    tipo_plan = models.CharField(max_length=200, null=True, blank=True, help_text="Especificar si se solicita plan especial")

    class Meta:
        db_table = 'alimentacion_nutricion'
        verbose_name = 'Alimentación y Nutrición'
        verbose_name_plural = 'Alimentación y Nutrición'

    def __str__(self):
        return f"Alimentación y Nutrición - CUS {self.cus.id}"
    

#EXAMEN OFTALMOLOGICO 
class ExamenOftalmologico(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='oftalmologico')

    agudeza_visual_der = models.CharField(max_length=20, null=True, blank=True)
    agudeza_visual_izq = models.CharField(max_length=20, null=True, blank=True)
    usa_anteojos = models.BooleanField(null=True, blank=True)
    otros = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'examen_oftalmologico'
        verbose_name = 'Examen Oftalmológico'
        verbose_name_plural = 'Exámenes Oftalmológicos'

    def __str__(self):
        return f"Examen Oftalmológico - CUS {self.cus.id}"
    
#EXAMEN FONOAUDILOGICO
class ExamenFonoaudiologico(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='fonoaudiologico')
    detalles = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'examen_fonoaudiologico'
        verbose_name = 'Examen Fonoaudiológico'
        verbose_name_plural = 'Exámenes Fonoaudiológicos'

    def __str__(self):
        return f"Fonoaudiología - CUS {self.cus.id}"
    
#EXAMEN PIEL/TAC
class ExamenPiel(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='piel')
    detalles = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'examen_piel_tcsc'
        verbose_name = 'Examen de Piel y T.C.S.C.'
        verbose_name_plural = 'Exámenes de Piel y T.C.S.C.'

    def __str__(self):
        return f"Examen de Piel - CUS {self.cus.id}"
    
#EXAMEN ODONTOOGICO
class ExamenOdontologico(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='odontologico')
    detalles = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'examen_odontologico'
        verbose_name = 'Examen Odontológico'
        verbose_name_plural = 'Exámenes Odontológicos'

    def __str__(self):
        return f"Examen Odontológico - CUS {self.cus.id}"
#EXAMEN CARIOVASCULAR
class ExamenCardiovascular(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='cardiovascular')

    auscultacion = models.CharField(max_length=255, null=True, blank=True)
    arritmia = models.CharField(max_length=255, null=True, blank=True)
    soplos = models.CharField(max_length=255, null=True, blank=True)
    tension_arterial = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'examen_cardiovascular'
        verbose_name = 'Examen Cardiovascular'
        verbose_name_plural = 'Exámenes Cardiovasculares'

    def __str__(self):
        return f"Cardiovascular - CUS {self.cus.id}"

#EXAMEN RESPIRATORIO 
class ExamenRespiratorio(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='respiratorio')
    detalles = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'examen_respiratorio'
        verbose_name = 'Examen Respiratorio'
        verbose_name_plural = 'Exámenes Respiratorios'

    def __str__(self):
        return f"Respiratorio - CUS {self.cus.id}"

# EXAMEN ABDOMEN

class ExamenAbdomen(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='abdomen')
    detalles = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'examen_abdomen'
        verbose_name = 'Examen Abdomen'
        verbose_name_plural = 'Exámenes Abdomen'

    def __str__(self):
        return f"Abdomen - CUS {self.cus.id}"


# EXAMEN GENITOURINARIO
class ExamenGenitourinario(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='genitourinario')
    
    menarca = models.BooleanField(null=True, blank=True)
    turner = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = 'examen_genitourinario'
        verbose_name = 'Examen Genitourinario'
        verbose_name_plural = 'Exámenes Genitourinarios'

    def __str__(self):
        return f"Genitourinario - CUS {self.cus.id}"
# EXAMEN ENDOCRINOLOGO
class ExamenEndocrinologico(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='endocrino')
    detalles = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'examen_endocrinologico'
        verbose_name = 'Examen Endocrinológico'
        verbose_name_plural = 'Exámenes Endocrinológicos'

    def __str__(self):
        return f"Endocrinológico - CUS {self.cus.id}"
# EXAMEN OSTEOARTICUAR
class ExamenOsteoarticular(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='osteoarticular')

    columna_normal = models.BooleanField(null=True, blank=True)
    cifosis = models.BooleanField(null=True, blank=True)
    lordosis = models.BooleanField(null=True, blank=True)
    escoliosis = models.BooleanField(null=True, blank=True)

    miembros_superiores = models.TextField(null=True, blank=True)
    miembros_inferiores = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'examen_osteoarticular'
        verbose_name = 'Examen Osteoarticular'
        verbose_name_plural = 'Exámenes Osteoarticulares'

    def __str__(self):
        return f"Osteoarticular - CUS {self.cus.id}"
# EXAMEN NEUROLOGICO

class ExamenNeurologico(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='neurologico')
    detalles = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'examen_neurologico'
        verbose_name = 'Examen Neurológico'
        verbose_name_plural = 'Exámenes Neurológicos'

    def __str__(self):
        return f"Neurológico - CUS {self.cus.id}"

# ESTUDIOS MEDICOS 
def default_fecha_caducidad():
    return now().date() + timedelta(days=304)  # 10 meses

class EstudioCus(models.Model):
    TIPO_ESTUDIO = [
        ('ELECTRO', 'Electrocardiograma'),
        ('OTROS', 'Otros Estudios'),
    ]

    id = models.AutoField(primary_key=True)
    cus = models.ForeignKey('Cus', on_delete=models.CASCADE, related_name="estudios")

    tipo_estudio = models.CharField(max_length=20, choices=TIPO_ESTUDIO)
    archivo = models.FileField(upload_to='estudios_cus/', null=True, blank=True)
    observaciones = models.CharField(max_length=200, null=True, blank=True)

    fecha_creacion = models.DateTimeField(default=now, editable=False)
    fecha_caducidad = models.DateField(default=default_fecha_caducidad)

    class Meta:
        db_table = 'estudios_cus'
        verbose_name = 'Estudio CUS'
        verbose_name_plural = 'Estudios CUS'

    def __str__(self):
        return f'{self.get_tipo_estudio_display()} - {self.cus.estudiante.nombre} {self.cus.estudiante.apellido}'    


#COMENTARIOS Y DERIVACIONES
class ComentarioDerivacion(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='comentarios')

    comentarios = models.TextField(null=True, blank=True, verbose_name="Comentarios y/o derivaciones")
    recomendaciones = models.TextField(null=True, blank=True, verbose_name="Se recomienda")

    class Meta:
        db_table = 'comentarios_derivaciones'
        verbose_name = 'Comentarios y Derivaciones'
        verbose_name_plural = 'Comentarios y Derivaciones'

    def __str__(self):
        return f"Comentarios - CUS {self.cus.id}"



# RECOMENDACIONES
class Recomendaciones(models.Model):
    cus = models.OneToOneField('Cus', on_delete=models.CASCADE, related_name='recomendaciones')
    detalles = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'recomendaciones'
        verbose_name = 'Recomendaciones'
        verbose_name_plural = 'Recomendaciones'

    def __str__(self):
        return f"Recomendaciones - CUS {self.cus.id}"