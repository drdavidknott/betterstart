# Generated by Django 3.0.3 on 2020-02-22 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0066_auto_20200222_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboard_panel_spec',
            name='prebuilt_panel',
            field=models.CharField(blank=True, choices=[('Parent_Exceptions_Panel', 'Parent Exceptions'), ('Age_Status_Exceptions_Panel', 'Age Status Exceptions')], default='', max_length=50),
        ),
    ]
