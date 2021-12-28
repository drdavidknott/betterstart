# Generated by Django 3.1.13 on 2021-12-28 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0182_auto_20211228_0729'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='survey',
            options={'ordering': ['name'], 'verbose_name_plural': 'survey'},
        ),
        migrations.AlterModelOptions(
            name='survey_series',
            options={'ordering': ['name'], 'verbose_name_plural': 'survey series'},
        ),
        migrations.RenameField(
            model_name='survey',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='survey_section',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='survey_series',
            old_name='title',
            new_name='name',
        ),
    ]