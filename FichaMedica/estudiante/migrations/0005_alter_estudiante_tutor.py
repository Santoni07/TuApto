# Generated by Django 5.1.1 on 2025-03-25 19:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiante', '0004_antecedentescus_declaracion_jurada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudiante',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estudiantes', to='estudiante.tutor'),
        ),
    ]
