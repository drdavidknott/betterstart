# Generated by Django 3.0.2 on 2020-02-04 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0049_auto_20200204_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboard_column_spec',
            name='date_field',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='dashboard_column_spec',
            name='date_filter',
            field=models.CharField(blank=True, choices=[('', 'no date filter'), ('this_month', 'this month'), ('last_month', 'last_month'), ('this_project_year', 'this project year'), ('last_project_year', 'last project year'), ('this_calendar_year', 'this calendar year'), ('last_calendar_year', 'last_calendar_year')], default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='dashboard_column_spec',
            name='title',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
