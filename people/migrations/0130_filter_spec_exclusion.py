# Generated by Django 3.0.7 on 2020-06-09 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0129_auto_20200608_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter_spec',
            name='exclusion',
            field=models.BooleanField(default=False),
        ),
    ]
