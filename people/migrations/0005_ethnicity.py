# Generated by Django 2.1.5 on 2019-03-03 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0004_auto_20190217_1617'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ethnicity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'ethnicities',
            },
        ),
    ]