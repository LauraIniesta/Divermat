# Generated by Django 3.0 on 2023-02-25 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0031_auto_20230218_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='ejerciciousuario',
            name='resultado',
            field=models.CharField(default=None, max_length=1000),
        ),
    ]
