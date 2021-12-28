# Generated by Django 3.1.13 on 2021-12-28 10:12

from django.db import migrations, models
import django.db.models.deletion
import people.django_extensions


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0184_survey_question_survey_question_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='survey_question',
            options={'ordering': ['survey_section__survey__name', 'survey_section__name', 'number'], 'verbose_name_plural': 'survey questions'},
        ),
        migrations.CreateModel(
            name='Survey_Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.person')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.survey')),
            ],
            options={
                'verbose_name_plural': 'survey submissions',
                'ordering': ['-date'],
            },
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Survey_Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('range_answer', models.IntegerField(default=0)),
                ('text_answer', models.CharField(blank=True, default='', max_length=500)),
                ('survey_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.survey_question')),
                ('survey_submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.survey_submission')),
            ],
            options={
                'verbose_name_plural': 'survey answers',
                'ordering': ['-survey_submission__date', '-survey_question__number'],
            },
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
    ]
