# Generated by Django 3.0.3 on 2020-02-16 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0058_auto_20200216_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard_column_spec',
            name='width',
            field=models.IntegerField(default=4),
        ),
        migrations.AddField(
            model_name='dashboard_spec',
            name='margin',
            field=models.IntegerField(default=1),
        ),
    ]
