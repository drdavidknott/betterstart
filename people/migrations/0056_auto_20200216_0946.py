# Generated by Django 3.0.2 on 2020-02-16 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0055_auto_20200208_1502'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Dashboard_Column_Inclusion',
            new_name='Dashboard_Panel_Column_Inclusion',
        ),
        migrations.RenameModel(
            old_name='Dashboard_Column_Spec',
            new_name='Dashboard_Panel_Column_Spec',
        ),
        migrations.AlterModelOptions(
            name='dashboard_panel_column_inclusion',
            options={'verbose_name_plural': 'dashboard panel column inclusions'},
        ),
        migrations.AlterModelOptions(
            name='dashboard_panel_column_spec',
            options={'ordering': ['title'], 'verbose_name_plural': 'dashboard panel column specs'},
        ),
    ]