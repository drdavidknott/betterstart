# Generated by Django 3.1.14 on 2022-07-23 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0192_age_status_use_for_automated_categorisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='has_trained_roles',
            field=models.BooleanField(default=True),
        ),
    ]
