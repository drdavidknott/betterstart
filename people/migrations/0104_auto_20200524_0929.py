# Generated by Django 3.0.3 on 2020-05-24 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0103_auto_20200516_1722'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('order',), 'verbose_name_plural': 'questions'},
        ),
        migrations.AddField(
            model_name='question',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]