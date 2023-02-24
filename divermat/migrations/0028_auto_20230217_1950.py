# Generated by Django 3.0 on 2023-02-17 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0027_examen_cronometrado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examen',
            name='tiempo',
        ),
        migrations.CreateModel(
            name='Foto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('perfil', models.BooleanField(default=False, max_length=50)),
                ('foto', models.FileField(blank=True, upload_to='media/fotos/%y')),
                ('curso', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='divermat.Curso')),
                ('tema', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='divermat.Tema')),
            ],
            options={
                'ordering': ('curso', 'tema'),
            },
        ),
    ]
