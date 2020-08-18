# Generated by Django 3.0.7 on 2020-08-18 07:06

from django.db import migrations, models
import django.db.models.deletion
import people.django_extensions


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0149_trained_role_date_trained'),
    ]

    operations = [
        migrations.CreateModel(
            name='Printform_Data_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'printform data types',
            },
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
        migrations.AlterModelOptions(
            name='street',
            options={'ordering': ('name',), 'verbose_name_plural': 'streets'},
        ),
        migrations.CreateModel(
            name='Printform_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=50)),
                ('order', models.IntegerField(default=0)),
                ('printform_data_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Printform_Data_Type')),
            ],
            options={
                'verbose_name_plural': 'printform data',
                'ordering': ['printform_data_type__name', 'order'],
            },
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
    ]
