# Generated by Django 2.2.4 on 2019-10-13 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0031_person_abss_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='ABSS_end_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]
