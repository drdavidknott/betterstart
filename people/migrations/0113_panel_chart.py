# Generated by Django 3.0.7 on 2020-06-05 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0112_auto_20200530_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='panel',
            name='chart',
            field=models.CharField(blank=True, choices=[('Test Chart', 'Test Chart')], default='', max_length=50),
        ),
    ]
