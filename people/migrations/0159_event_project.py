# Generated by Django 3.0.7 on 2020-11-15 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0158_auto_20201114_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='people.Project'),
        ),
    ]
