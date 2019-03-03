# Generated by Django 2.1.5 on 2019-02-17 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Relationship_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'verbose_name_plural': 'people'},
        ),
        migrations.AlterField(
            model_name='person',
            name='notes',
            field=models.TextField(default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='relationship',
            name='relationship_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rel_from', to='people.Person'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='relationship_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rel_to', to='people.Person'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='relationship_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Relationship_Type'),
        ),
        migrations.AddField(
            model_name='person',
            name='relationships',
            field=models.ManyToManyField(through='people.Relationship', to='people.Person'),
        ),
    ]
