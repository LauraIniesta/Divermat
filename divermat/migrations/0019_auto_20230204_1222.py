# Generated by Django 3.0 on 2023-02-04 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0018_resumen_resumen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(blank=True, upload_to='media/videos/%y'),
        ),
    ]
