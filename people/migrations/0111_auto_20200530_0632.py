# Generated by Django 3.0.3 on 2020-05-30 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0110_auto_20200530_0631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='password_reset_email_from',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='site',
            name='password_reset_email_title',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
