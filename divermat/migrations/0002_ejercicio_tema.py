# Generated by Django 3.0 on 2022-05-23 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ejercicio',
            name='tema',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='divermat.Tema'),
        ),
    ]
