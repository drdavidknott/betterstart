# Generated by Django 2.2.4 on 2019-11-24 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0034_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='navbar_text',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]