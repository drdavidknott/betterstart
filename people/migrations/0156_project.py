# Generated by Django 3.0.7 on 2020-11-08 11:13

from django.db import migrations, models
import people.django_extensions


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0155_auto_20201101_0801'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('navbar_background', models.CharField(blank=True, max_length=50)),
                ('navbar_text', models.CharField(blank=True, default=None, max_length=50, null=True)),
            ],
            bases=(people.django_extensions.DataAccessMixin, models.Model),
        ),
    ]