# Generated by Django 3.1.9 on 2021-06-12 05:30

from django.db import migrations, models
import django.db.models.deletion
import people.django_extensions


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0173_auto_20210606_1026'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question_Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'sections',
                'ordering': ('order',),
            },
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
        migrations.AddField(
            model_name='question',
            name='question_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='people.venue'),
        ),
    ]
