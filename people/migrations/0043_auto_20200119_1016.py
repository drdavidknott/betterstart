# Generated by Django 3.0 on 2020-01-19 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0042_site_messages'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ('last_name', 'first_name'), 'verbose_name_plural': 'people'},
        ),
    ]
