# Generated by Django 3.0 on 2023-01-22 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0008_ejercicio_solucion_correcta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examen',
            name='ejercicios',
            field=models.ManyToManyField(to='divermat.Ejercicio'),
        ),
        migrations.AlterField(
            model_name='examen',
            name='temas',
            field=models.ManyToManyField(to='divermat.Tema'),
        ),
    ]
