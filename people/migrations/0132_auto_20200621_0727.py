# Generated by Django 3.0.7 on 2020-06-21 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0131_site_password_reset_email_cc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(max_length=1500),
        ),
        migrations.AlterField(
            model_name='venue',
            name='contact_name',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='opening_hours',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='price',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='website',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
