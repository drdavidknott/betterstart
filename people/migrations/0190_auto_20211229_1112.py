# Generated by Django 3.1.13 on 2021-12-29 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0189_survey_question_type_text_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey_question',
            name='options',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
