# Generated by Django 3.0.7 on 2020-06-28 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0136_auto_20200628_1048'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invitation_step',
            options={'ordering': ['invitation_step_type__order'], 'verbose_name_plural': 'invitation steps'},
        ),
    ]