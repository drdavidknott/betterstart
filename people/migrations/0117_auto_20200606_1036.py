# Generated by Django 3.0.7 on 2020-06-06 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0116_chart_label_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='label_field',
            field=models.CharField(max_length=50),
        ),
    ]
