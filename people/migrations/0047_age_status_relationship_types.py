# Generated by Django 3.0.2 on 2020-01-26 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0046_site_dob_offset'),
    ]

    operations = [
        migrations.AddField(
            model_name='age_status',
            name='relationship_types',
            field=models.ManyToManyField(to='people.Relationship_Type'),
        ),
    ]