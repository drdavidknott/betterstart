# Generated by Django 3.0.7 on 2020-07-18 05:51

from django.db import migrations, models
import people.django_extensions


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0141_question_use_for_children_form'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration_Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('title', models.TextField(blank=True, default='', max_length=150)),
            ],
            options={
                'verbose_name_plural': 'registration forms',
            },
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
    ]
