# Generated by Django 3.0.3 on 2020-02-17 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0062_dashboard_column_spec_heading'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard_panel_column_spec',
            name='count_model',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='dashboard_panel_column_spec',
            name='count_field',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='filter_spec',
            name='filter_type',
            field=models.CharField(blank=True, choices=[('string', 'string'), ('boolean', 'boolean'), ('period', 'period'), ('object', 'object')], default='', max_length=50),
        ),
    ]