# Generated by Django 5.1.1 on 2025-04-18 10:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estudiante', '0006_alter_antecedentescus_estudiante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='antecedentescus',
            name='estudiante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='antecedentes', to='estudiante.estudiante'),
        ),
    ]
