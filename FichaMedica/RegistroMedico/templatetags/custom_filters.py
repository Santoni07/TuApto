from django import template

register = template.Library()

# Filtro personalizado para agregar una clase CSS a un campo de formulario
@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})