# Generated by Django 3.0.7 on 2020-12-12 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0163_auto_20201212_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='ethnicity',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]
