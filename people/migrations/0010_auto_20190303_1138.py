# Generated by Django 2.1.5 on 2019-03-03 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0009_auto_20190303_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house_name_or_number', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=50)),
                ('town', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'areas',
            },
        ),
        migrations.CreateModel(
            name='Post_Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_code', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name_plural': 'post codes',
            },
        ),
        migrations.CreateModel(
            name='Residence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Address')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person')),
            ],
            options={
                'verbose_name_plural': 'residences',
            },
        ),
        migrations.CreateModel(
            name='Ward',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ward_name', models.CharField(max_length=50)),
                ('area', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Area')),
            ],
            options={
                'verbose_name_plural': 'wards',
            },
        ),
        migrations.AlterModelOptions(
            name='cc_registration',
            options={'verbose_name_plural': 'children centre registrations'},
        ),
        migrations.AddField(
            model_name='post_code',
            name='ward',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Ward'),
        ),
        migrations.AddField(
            model_name='address',
            name='post_code',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Post_Code'),
        ),
        migrations.AddField(
            model_name='person',
            name='addresses',
            field=models.ManyToManyField(through='people.Residence', to='people.Address'),
        ),
    ]
