# Generated by Django 3.0.7 on 2020-08-10 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0143_auto_20200718_0659'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='use_for_invitations_additional_info',
            field=models.BooleanField(default=False),
        ),
    ]
