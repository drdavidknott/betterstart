# Generated by Django 3.0 on 2019-12-15 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0038_event_registration_apologies'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='nicknames',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='person',
            name='prior_names',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
