# Generated by Django 3.0 on 2023-02-25 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0033_auto_20230225_0944'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ejerciciousuario',
            name='resultado',
        ),
    ]
