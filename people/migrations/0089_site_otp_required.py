# Generated by Django 3.0.3 on 2020-04-13 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0088_auto_20200405_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='otp_required',
            field=models.BooleanField(default=False),
        ),
    ]