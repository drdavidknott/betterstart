# Generated by Django 3.1.9 on 2021-06-06 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0172_question_projects'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='projects',
            field=models.ManyToManyField(blank=True, to='people.Project'),
        ),
    ]