# Generated by Django 2.1.5 on 2019-03-03 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0011_auto_20190303_1208'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event_registration',
            options={'verbose_name_plural': 'event registrations'},
        ),
        migrations.RemoveField(
            model_name='person',
            name='age_status',
        ),
    ]