# Generated by Django 3.0.3 on 2020-04-04 05:26

from django.db import migrations, models
import django.db.models.deletion
import people.django_extensions


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0084_auto_20200329_1057'),
    ]

    operations = [
        migrations.CreateModel(
            name='Venue_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'venue types',
            },
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('building_name_or_number', models.CharField(max_length=50)),
                ('street', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='people.Street')),
            ],
            options={
                'verbose_name_plural': 'venues',
            },
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
    ]