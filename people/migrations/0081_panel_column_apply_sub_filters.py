# Generated by Django 3.0.3 on 2020-03-08 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0080_panel_sub_filters'),
    ]

    operations = [
        migrations.AddField(
            model_name='panel_column',
            name='apply_sub_filters',
            field=models.BooleanField(default=True),
        ),
    ]
