# Generated by Django 3.0.3 on 2020-04-05 05:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0086_venue_venue_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='venue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='people.Venue'),
        ),
    ]