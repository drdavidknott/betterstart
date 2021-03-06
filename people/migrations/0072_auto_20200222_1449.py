# Generated by Django 3.0.3 on 2020-02-22 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0071_auto_20200222_1338'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Dashboard_Panel_Spec',
            new_name='Panel',
        ),
        migrations.AlterModelOptions(
            name='column_in_dashboard',
            options={'verbose_name_plural': 'columns in dashboards'},
        ),
        migrations.AlterModelOptions(
            name='panel_column_in_panel',
            options={'verbose_name_plural': 'panel columns in panels'},
        ),
        migrations.AlterModelOptions(
            name='panel_in_column',
            options={'verbose_name_plural': 'panels in columns'},
        ),
        migrations.RenameField(
            model_name='panel_column_in_panel',
            old_name='dashboard_panel_spec',
            new_name='panel',
        ),
        migrations.RenameField(
            model_name='panel_in_column',
            old_name='dashboard_panel_spec',
            new_name='panel',
        ),
    ]
