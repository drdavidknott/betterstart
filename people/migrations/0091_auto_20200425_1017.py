# Generated by Django 3.0.3 on 2020-04-25 09:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0090_auto_20200425_0714'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invitation',
            options={'verbose_name_plural': 'invitations'},
        ),
        migrations.AlterModelOptions(
            name='invitation_step',
            options={'verbose_name_plural': 'invitation steps'},
        ),
        migrations.AlterModelOptions(
            name='invitation_step_type',
            options={'ordering': ('order',), 'verbose_name_plural': 'invitation step types'},
        ),
        migrations.AlterModelOptions(
            name='terms_and_conditions',
            options={'verbose_name_plural': 'terms and conditions'},
        ),
        migrations.RemoveField(
            model_name='invitation',
            name='completed',
        ),
        migrations.AddField(
            model_name='invitation',
            name='datetime_completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invitation',
            name='datetime_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
