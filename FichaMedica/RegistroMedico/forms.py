from django import forms
from .models import *

class RegistroMedicoForm(forms.ModelForm):
    class Meta:
        model = RegistroMedico
        fields = [
            'jugador',
            'torneo',
            'estado',
            
            'fecha_caducidad',
            'observacion',
            'consentimiento_persona',
        ]
        widgets = {
            'fecha_caducidad': forms.SelectDateWidget(),  # Widget para selección de fecha
            'observacion': forms.Textarea(attrs={'rows': 4, 'cols': 40}),  # Textarea para observaciones
        }

class AntecedenteEnfermedadesForm(forms.ModelForm):
    class Meta:
        model = AntecedenteEnfermedades
        exclude = ['alerg_observ', 'fhd_observacion', 'cca_observaciones','idfichaMedica']
        labels = {
            'fue_operado': '¿Fue operado en los últimos 4 meses?',
            'toma_medicacion': '¿Toma regularmente alguna medicación?',
            'estuvo_internado': '¿Estuvo internado en el último año?',
            'sufre_hormigueos': '¿Sufre de hormigueos en las manos?',
            'es_diabetico': '¿Es diabético?',
            'es_amatico': '¿Es asmático?',
            'es_alergico': '¿Es alérgico?',
            'alerg_observ': 'Observaciones de alergias',
            'antecedente_epilepsia': '¿Tiene antecedentes de epilepsia o convulsiones?',
            'desviacion_columna': '¿Tiene desviación de columna?',
            'dolor_cintira': '¿Tiene dolor de cintura después de realizar ejercicios físicos?',
            'fracturas': '¿Ha tenido fracturas, luxaciones o lesiones ligamentarias en los últimos 4 meses?',
            'dolores_articulares': '¿Tiene dolores articulares?',
            'falta_aire': '¿Alguna vez experimentó falta de aire excesiva mientras realizaba ejercicios físicos?',
            'tramatismos_craneo': '¿Ha tenido traumatismos de cráneo con pérdida de conocimiento en los últimos 4 meses?',
            'dolor_pecho': '¿Alguna vez sintió dolor en el pecho mientras realizaba ejercicios físicos o después?',
            'perdida_conocimiento': '¿Alguna vez perdió el conocimiento durante ejercicios físicos o después?',
            'presion_arterial': '¿Le han detectado alguna vez presión arterial alta?',
            'muerte_subita_familiar': '¿Algún familiar ha sufrido muerte súbita antes de los 45 años?',
            'enfermedad_cardiaca_familiar': '¿Familiar directo con antecedentes de enfermedad cardíaca, Síndrome de Marfán?',
            'soplo_cardiaco': '¿Le han detectado alguna vez un soplo cardíaco?',
            'abstenerce_competencia': '¿Algún médico le ha recomendado abstenerse de competir?',
            'antecedentes_coronarios_familiares': '¿Familiares menores de 65 años con antecedentes coronarios?',
            'fumar_hipertension_diabetes': '¿Fuma, tiene hipertensión, diabetes o colesterol alto?',
            'fhd_observacion': 'Observaciones sobre FHD',
            'consumo_cocaina_anabolicos': '¿Consumo de cocaína o anabólicos?',
            'cca_observaciones': 'Observaciones sobre consumo de cocaína o anabólicos'
        }
        widgets = {
            'alerg_observ': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'fhd_observacion': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'cca_observaciones': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        }

class EstudioMedicoForm(forms.ModelForm):
    class Meta:
        model = EstudiosMedico
        fields = ['tipo_estudio', 'observaciones', 'archivo']  # Elimina el espacio adicional en 'observaciones'
        
        # Definimos los widgets para personalizar la apariencia de los campos en el formulario
        widgets = {
            'tipo_estudio': forms.Select(attrs={'class': 'form-control'}),  
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),  
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),  
        } 

class ElectroBasalForm(forms.ModelForm):
    class Meta:
        model = ElectroBasal
        fields = [
            'ritmo', 'PQ', 'frecuencia', 'arritmias', 'ejeQRS', 
            'trazadoNormal', 'observaciones'
        ]
        widgets = {
            'ritmo': forms.TextInput(attrs={'class': 'form-control'}),
            'PQ': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia': forms.TextInput(attrs={'class': 'form-control'}),
            'arritmias': forms.TextInput(attrs={'class': 'form-control'}),
            'ejeQRS': forms.TextInput(attrs={'class': 'form-control'}),
            'trazadoNormal': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # Define las opciones para 'trazadoNormal'
    TRAZADO_CHOICES = [
        ('Sí', 'Sí'),
        ('No', 'No'),
    ]
    
    trazadoNormal = forms.ChoiceField(choices=TRAZADO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))





class CardiovascularForm(forms.ModelForm):
    class Meta:
        model = Cardiovascular
        fields = [
            'auscultacion', 'soplos', 'R1', 'tension_arterial', 'R2', 
            'observaciones', 'ruidos_agregados'
        ]
        widgets = {
            'auscultacion': forms.TextInput(attrs={'class': 'form-control'}),
            'R1': forms.TextInput(attrs={'class': 'form-control'}),
            'R2': forms.TextInput(attrs={'class': 'form-control'}),
            'soplos': forms.TextInput(attrs={'class': 'form-control'}),
            'tension_arterial': forms.TextInput(attrs={'class': 'form-control'}),
            'ruidos_agregados': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            
            
        }


class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorio
        fields = [
            'citologico', 'orina', 'colesterol', 'uremia', 'glucemia', 
            'otros' 
        ]
        widgets = {
            'citologico': forms.TextInput(attrs={'class': 'form-control'}),
            'orina': forms.TextInput(attrs={'class': 'form-control'}),
            'colesterol': forms.TextInput(attrs={'class': 'form-control'}),
            'uremia': forms.TextInput(attrs={'class': 'form-control'}),
            'glucemia': forms.TextInput(attrs={'class': 'form-control'}),
            'otros': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ToraxForm(forms.ModelForm):
    class Meta:
        model = Torax
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
class ElectroEsfuerzoForm(forms.ModelForm):
    class Meta:
        model = ElectroEsfuerzo
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OftalmologicoForm(forms.ModelForm):
    class Meta:
        model = Oftalmologico
        fields = ['od', 'oi']
        widgets = {
            'od': forms.TextInput(attrs={'class': 'form-control'}),
            'oi': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RegistroMedicoUpdateForm(forms.ModelForm):
    class Meta:
        model = RegistroMedico
        fields = ['estado', 'observacion', 'fecha_de_llenado', 'fecha_caducidad', 'medico']
        widgets = {
            'fecha_de_llenado': forms.DateInput(attrs={'type': 'date'}),
            'fecha_caducidad': forms.DateInput(attrs={'type': 'date'}),
        } 


class OtrosExamenesClinicosForm(forms.ModelForm):
    class Meta:
        model = OtrosExamenesClinicos
        exclude = ['ficha_medica']
        fields = [
            'respiratorio_observaciones',
            'renal_observaciones',
            'digestivo_observaciones',
            'osteoarticular_observaciones',
            'ficha_medica'
        ]
        widgets = {
            'respiratorio_observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,'placeholder': 'Ingrese observaciones respiratorias...'}),

            'renal_observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,'placeholder': 'Ingrese observaciones renales...'}),
            'digestivo_observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,'placeholder': 'Ingrese observaciones digestivas...'}),
            'osteoarticular_observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,'placeholder': 'Ingrese observaciones osteoarticulares...'}),
        }
        labels = {
            'respiratorio_observaciones': 'Observaciones Respiratorias',
            'renal_observaciones': 'Observaciones Renales',
            'digestivo_observaciones': 'Observaciones Digestivas',
            'osteoarticular_observaciones': 'Observaciones Osteoarticulares',
        }
