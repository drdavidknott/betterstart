# Generated by Django 2.2.4 on 2019-09-07 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0026_auto_20190906_0756'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trained_role',
            options={'verbose_name_plural': 'trained roles'},
        ),
        migrations.AlterField(
            model_name='trained_role',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
