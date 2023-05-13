# Generated by Django 3.0 on 2023-01-28 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0009_auto_20230122_1815'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examen',
            name='ejercicios',
        ),
        migrations.CreateModel(
            name='ExamenEjercicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ejercicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='divermat.Ejercicio')),
                ('examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='divermat.Examen')),
            ],
        ),
    ]
