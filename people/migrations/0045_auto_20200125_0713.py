# Generated by Django 3.0.2 on 2020-01-25 07:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0044_auto_20200119_1125'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='nicknames',
            new_name='other_names',
        ),
    ]
