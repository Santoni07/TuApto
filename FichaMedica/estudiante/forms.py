from django import forms
from .models import AntecedentesCUS, Tutor, Estudiante, Colegio, EstudianteColegio

class TutorForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['profile', 'domicilio', 'telefono', 'localidad']
        widgets = {
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'localidad': forms.TextInput(attrs={'class': 'form-control'}),
        }
class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = [
            'nombre', 'apellido', 'fecha_nacimiento', 'dni', 'domicilio',
            'telefono', 'sexo', 'localidad', 'lugar_nacimiento'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'localidad': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk:  # Ya existe: estamos editando, no creando
            original = Estudiante.objects.get(pk=self.instance.pk)
            for field in self.fields:
                nuevo_valor = getattr(instance, field)
                if not nuevo_valor:  # Si no se envió o está vacío, restaurar el original
                    setattr(instance, field, getattr(original, field))
        if commit:
            instance.save()
        return instance
    
    
class ColegioForm(forms.ModelForm):
    class Meta:
        model = Colegio
        fields = ['nombre', 'direccion', 'telefono', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class EstudianteColegioForm(forms.ModelForm):
    class Meta:
        model = EstudianteColegio
        fields = ['estudiante', 'colegio', 'activo']
        widgets = {
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AntecedentesCUSForm(forms.ModelForm):
    class Meta:
        model = AntecedentesCUS
        exclude = ['estudiante']  # Este campo lo asignás manualmente
        fields = [
            # Relación con el estudiante
            'estudiante', 

            # 1. VACUNACIONES
            'carnet_vacunacion', 'esquema_completo', 'esquema_faltante',

            # 2. ANTECEDENTES PATOLÓGICOS
            'enfermedades_importantes', 'cirugias', 'cardiovasculares', 'trauma_funcional',
            'alergias', 'oftalmologicos', 'auditivos', 'diabetes', 'asma', 'chagas', 
            'hipertension', 'neurologico', 'otras',

            # 3. CONDICIONES DE RIESGO
            'condiciones_riesgo',

            # 4. MEDICAMENTOS PRESCRIPTOS
            'medicamentos_prescriptos',

            # 5. DURANTE ACTIVIDAD FÍSICA PREVIA SUFRIÓ:
            'cansancio_extremo', 'falta_aire', 'perdida_conocimiento', 'palpitaciones',
            'precordialgias', 'cefaleas', 'vomitos', 'otros'
            # 6 Declaracion jurada 
            ,'declaracion_jurada'
        ]

        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-control'}),
            'carnet_vacunacion': forms.Select(choices=[(True, 'Sí'), (False, 'No')], attrs={'class': 'form-control'}),
            'esquema_completo': forms.Select(choices=[(True, 'Sí'), (False, 'No')], attrs={'class': 'form-control'}),
            'esquema_faltante': forms.TextInput(attrs={'class': 'form-control'}),
            'declaracion_jurada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Textareas
            'enfermedades_importantes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'otras': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            
            # TextInputs
            'cirugias': forms.TextInput(attrs={'class': 'form-control'}),
            'cardiovasculares': forms.TextInput(attrs={'class': 'form-control'}),
            'trauma_funcional': forms.TextInput(attrs={'class': 'form-control'}),
            'alergias': forms.TextInput(attrs={'class': 'form-control'}),
            'oftalmologicos': forms.TextInput(attrs={'class': 'form-control'}),
            'auditivos': forms.TextInput(attrs={'class': 'form-control'}),
            'condiciones_riesgo': forms.TextInput(attrs={'class': 'form-control'}),
            'medicamentos_prescriptos': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AntecedentesCUSForm, self).__init__(*args, **kwargs)

        # Campos tipo Select (Sí/No) para valores booleanos
        boolean_fields = [
            'diabetes', 'asma', 'chagas', 'hipertension', 'neurologico',
            'cansancio_extremo', 'falta_aire', 'perdida_conocimiento', 'palpitaciones',
            'precordialgias', 'cefaleas', 'vomitos'
        ]
        for field in boolean_fields:
            self.fields[field].widget = forms.Select(
    choices=[(True, 'Sí'), (False, 'No')],
    attrs={
        'class': 'form-select form-select-sm mx-auto d-block',
        'style': 'width: 100px;'  # o menos si querés más compacto
    }
)

        # Estilo especial para el checkbox de declaración jurada
        self.fields['declaracion_jurada'].widget.attrs.update({
            'class': 'form-check-input fs-4 border border-3 border-secondary shadow-sm'
        })