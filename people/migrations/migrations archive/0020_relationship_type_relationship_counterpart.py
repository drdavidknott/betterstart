# Generated by Django 2.1.5 on 2019-03-17 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0019_person_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship_type',
            name='relationship_counterpart',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]