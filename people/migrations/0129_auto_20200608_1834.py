# Generated by Django 3.0.7 on 2020-06-08 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0128_auto_20200608_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='venue',
            name='notes',
            field=models.TextField(blank=True, default='', max_length=1500),
        ),
    ]
