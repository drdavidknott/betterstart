# Generated by Django 3.0.7 on 2020-06-08 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0126_auto_20200607_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='title',
            field=models.CharField(max_length=50),
        ),
    ]
