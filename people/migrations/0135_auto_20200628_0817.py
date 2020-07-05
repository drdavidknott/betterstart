# Generated by Django 3.0.7 on 2020-06-28 07:17

from django.db import migrations, models
import jsignature.fields


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0134_auto_20200627_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation_step',
            name='signature',
            field=jsignature.fields.JSignatureField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invitation_step',
            name='step_data',
            field=models.TextField(blank=True, default='', max_length=1500),
        ),
        migrations.AddField(
            model_name='invitation_step_type',
            name='data_type',
            field=models.CharField(blank=True, choices=[('string', 'string'), ('table', 'table'), ('signature', 'signature')], default='', max_length=50),
        ),
    ]