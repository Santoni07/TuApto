from django import forms
from .models import *
from datetime import date

# Reutilizables
def widget_input(): return forms.TextInput(attrs={'class': 'form-control'})
def widget_textarea(rows=2): return forms.Textarea(attrs={'class': 'form-control', 'rows': rows})
def widget_checkbox(): return forms.CheckboxInput(attrs={'class': 'form-check-input'})
def widget_select(): return forms.Select(attrs={'class': 'form-control'})
def widget_date(): return forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

# FORMULARIOS
class CusForm(forms.ModelForm):
    class Meta:
        model = Cus
        fields = ['estudiante', 'estado', 'fecha_caducidad', 'fecha_de_llenado', 'observacion', 'consentimiento_persona', 'medico']
        widgets = {
            'estudiante': widget_select(),
            'estado': widget_select(),
            'fecha_caducidad': forms.HiddenInput(),
            'fecha_de_llenado': widget_date(),
            'observacion': widget_input(),
            'consentimiento_persona': widget_checkbox(),
            'medico': widget_select(),
        }
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Solo si no hay instancia con valor ya cargado
            if not self.instance.pk or not self.instance.fecha_de_llenado:
                self.fields['fecha_de_llenado'].initial = date.today()
class ExamenFisicoForm(forms.ModelForm):
    imc = forms.DecimalField(
        label='IMC',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'id_imc'
        })
    )

    diagnostico_antropometrico = forms.CharField(
        label='Diagnóstico Antropométrico',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'id_diagnostico_antropometrico'
        })
    )

    class Meta:
        model = ExamenFisico
        fields = ['peso', 'talla', 'imc', 'diagnostico_antropometrico']
        widgets = {
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'id': 'id_peso'
            }),
            'talla': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'id': 'id_talla'
            }),
        }

class AlimentacionNutricionForm(forms.ModelForm):
    class Meta:
        model = AlimentacionNutricion
        fields = ['solicita_plan_especial', 'tipo_plan']
        widgets = {
            'solicita_plan_especial': widget_checkbox(),
            'tipo_plan': widget_input(),
        }

class ExamenOftalmologicoForm(forms.ModelForm):
    class Meta:
        model = ExamenOftalmologico
        fields = ['agudeza_visual_der', 'agudeza_visual_izq', 'usa_anteojos', 'otros']
        widgets = {
            'agudeza_visual_der': widget_input(),
            'agudeza_visual_izq': widget_input(),
            'usa_anteojos': widget_checkbox(),
            'otros': widget_input(),
        }

class ExamenFonoaudiologicoForm(forms.ModelForm):
    class Meta:
        model = ExamenFonoaudiologico
        fields = ['detalles']
        widgets = {'detalles': widget_textarea()}

class ExamenPielForm(forms.ModelForm):
    class Meta:
        model = ExamenPiel
        fields = ['detalles']
        widgets = {'detalles': widget_textarea()}

class ExamenOdontologicoForm(forms.ModelForm):
    class Meta:
        model = ExamenOdontologico
        fields = ['detalles']
        widgets = {'detalles': widget_textarea()}

class ExamenCardiovascularForm(forms.ModelForm):
    class Meta:
        model = ExamenCardiovascular
        fields = ['auscultacion', 'arritmia', 'soplos', 'tension_arterial']
        widgets = {
            'auscultacion': widget_input(),
            'arritmia': widget_input(),
            'soplos': widget_input(),
            'tension_arterial': widget_input(),
        }

class ExamenRespiratorioForm(forms.ModelForm):
    class Meta:
        model = ExamenRespiratorio
        fields = ['detalles']
        widgets = {'detalles': widget_textarea()}

class ExamenAbdomenForm(forms.ModelForm):
    class Meta:
        model = ExamenAbdomen
        fields = ['detalles']
        widgets = {'detalles': widget_textarea()}

class ExamenGenitourinarioForm(forms.ModelForm):
    class Meta:
        model = ExamenGenitourinario
        fields = ['menarca', 'turner']
        widgets = {
            'menarca': widget_checkbox(),
            'turner': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Normal, Sospecha, etc.'}),
        }

class ExamenEndocrinologicoForm(forms.ModelForm):
    class Meta:
        model = ExamenEndocrinologico
        fields = ['detalles']
        widgets = {'detalles': widget_textarea()}

class ExamenOsteoarticularForm(forms.ModelForm):
    class Meta:
        model = ExamenOsteoarticular
        fields = ['columna_normal', 'cifosis', 'lordosis', 'escoliosis', 'miembros_superiores', 'miembros_inferiores']
        widgets = {
            'columna_normal': widget_checkbox(),
            'cifosis': widget_checkbox(),
            'lordosis': widget_checkbox(),
            'escoliosis': widget_checkbox(),
            'miembros_superiores': widget_textarea(),
            'miembros_inferiores': widget_textarea(),
        }

class ExamenNeurologicoForm(forms.ModelForm):
    class Meta:
        model = ExamenNeurologico
        fields = ['detalles']
        widgets = {'detalles': widget_textarea()}

class EstudioCusForm(forms.ModelForm):
    class Meta:
        model = EstudioCus
        fields = ['tipo_estudio', 'archivo', 'observaciones']
        widgets = {
            'tipo_estudio': widget_select(),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'observaciones': widget_input(),
            'fecha_caducidad': widget_date(),
        }

class ComentarioDerivacionForm(forms.ModelForm):
    class Meta:
        model = ComentarioDerivacion
        fields = ['comentarios']
        widgets = {
            'comentarios': widget_textarea(3),
            
        }

class RecomendacionesForm(forms.ModelForm):
    class Meta:
        model = Recomendaciones
        fields = ['detalles']
        widgets = {'detalles': widget_textarea(3)}

        
class ActualizacionCUSForm(forms.ModelForm):
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Médico responsable"
    )
    class Meta:
        model = ActualizacionCUS
        exclude = ['cus', 'fecha', 'imc', 'diagnostico_antropometrico']
        widgets = {
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'talla': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'antecedentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'examen_fisico': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estado_salud_normal': forms.CheckboxInput(),
            'derivado_a': forms.TextInput(attrs={'class': 'form-control'}),
            'debe_volver': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            
        }
