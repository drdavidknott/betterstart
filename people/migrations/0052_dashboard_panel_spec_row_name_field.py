# Generated by Django 3.0.2 on 2020-02-08 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0051_auto_20200204_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard_panel_spec',
            name='row_name_field',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
