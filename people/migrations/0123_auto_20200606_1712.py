# Generated by Django 3.0.7 on 2020-06-06 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0122_auto_20200606_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='stack_filter_term',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='chart',
            name='stack_label_field',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='chart',
            name='stack_model',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='chart',
            name='chart_type',
            field=models.CharField(blank=True, choices=[('pie', 'Pie Chart'), ('bar', 'Bar Chart'), ('month_bar', 'Bar Chart by Month'), ('stacked_bar', 'Stacked Bar Chart')], default='', max_length=50),
        ),
    ]