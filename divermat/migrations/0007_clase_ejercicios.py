# Generated by Django 3.0 on 2023-01-08 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0006_seguimiento'),
    ]

    operations = [
        migrations.AddField(
            model_name='clase',
            name='ejercicios',
            field=models.ManyToManyField(default=None, to='divermat.Ejercicio'),
        ),
    ]
