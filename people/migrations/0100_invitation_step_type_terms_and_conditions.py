# Generated by Django 3.0.3 on 2020-05-16 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0099_auto_20200516_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation_step_type',
            name='terms_and_conditions',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='people.Terms_And_Conditions'),
        ),
    ]