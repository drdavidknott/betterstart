# Generated by Django 2.1.5 on 2019-04-28 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_auto_20190428_1037'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role_History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person')),
                ('role_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Role_Type')),
            ],
        ),
    ]
