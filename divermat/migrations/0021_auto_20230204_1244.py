# Generated by Django 3.0 on 2023-02-04 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divermat', '0020_auto_20230204_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(blank=True, upload_to='media/videos/%y'),
        ),
    ]