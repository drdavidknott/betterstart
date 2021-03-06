# Generated by Django 2.1.5 on 2019-03-03 10:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_person_ethnicity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trained', models.BooleanField()),
                ('active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Role_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_type_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='person',
            name='ethnicity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Ethnicity'),
        ),
        migrations.AddField(
            model_name='role',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person'),
        ),
        migrations.AddField(
            model_name='role',
            name='role_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Role_Type'),
        ),
        migrations.AddField(
            model_name='person',
            name='roles',
            field=models.ManyToManyField(through='people.Role', to='people.Role_Type'),
        ),
    ]
