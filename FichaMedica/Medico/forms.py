from django import forms
from .models import Documentos

class DocumentosForm(forms.ModelForm):
    class Meta:
        model = Documentos
        fields = ['certificado_matricula', 'certificado_firma_electronica', 'contrato_aceptado']
        widgets = {
            'contrato_aceptado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }