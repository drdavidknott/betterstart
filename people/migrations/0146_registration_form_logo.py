# Generated by Django 3.0.7 on 2020-08-12 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0145_auto_20200812_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration_form',
            name='logo',
            field=models.ImageField(null=True, upload_to='images'),
        ),
    ]
