# Generated by Django 3.0.2 on 2020-01-25 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0045_auto_20200125_0713'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='dob_offset',
            field=models.IntegerField(default=0),
        ),
    ]