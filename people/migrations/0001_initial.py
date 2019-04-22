# Generated by Django 2.1.5 on 2019-04-21 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house_name_or_number', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=50)),
                ('town', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'answers',
            },
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'areas',
            },
        ),
        migrations.CreateModel(
            name='Capture_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capture_type_name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'capture types',
            },
        ),
        migrations.CreateModel(
            name='CC_Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_date', models.DateField()),
            ],
            options={
                'verbose_name_plural': 'children centre registrations',
            },
        ),
        migrations.CreateModel(
            name='Children_Centre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('children_centre_name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'children centres',
            },
        ),
        migrations.CreateModel(
            name='Ethnicity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'ethnicities',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=500)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('location', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'events',
            },
        ),
        migrations.CreateModel(
            name='Event_Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=500)),
            ],
            options={
                'verbose_name_plural': 'event categories',
            },
        ),
        migrations.CreateModel(
            name='Event_Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registered', models.BooleanField()),
                ('participated', models.BooleanField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Event')),
            ],
            options={
                'verbose_name_plural': 'event registrations',
            },
        ),
        migrations.CreateModel(
            name='Event_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=500)),
                ('event_category', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Event_Category')),
            ],
            options={
                'verbose_name_plural': 'event types',
            },
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'families',
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_label', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'options',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('middle_names', models.CharField(blank=True, default='', max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email_address', models.CharField(blank=True, default='', max_length=50)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, default='', max_length=25)),
                ('notes', models.TextField(blank=True, default='', max_length=1000)),
                ('english_is_second_language', models.BooleanField(default=False)),
                ('pregnant', models.BooleanField(default=False)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('savs_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'people',
            },
        ),
        migrations.CreateModel(
            name='Post_Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_code', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name_plural': 'post codes',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name_plural': 'questions',
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rel_from', to='people.Person')),
                ('relationship_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rel_to', to='people.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Relationship_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_type', models.CharField(max_length=50)),
                ('relationship_counterpart', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'relationship types',
            },
        ),
        migrations.CreateModel(
            name='Residence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Address')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person')),
            ],
            options={
                'verbose_name_plural': 'residences',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trained', models.BooleanField()),
                ('active', models.BooleanField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Role_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_type_name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'role types',
            },
        ),
        migrations.CreateModel(
            name='Ward',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ward_name', models.CharField(max_length=50)),
                ('area', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Area')),
            ],
            options={
                'verbose_name_plural': 'wards',
            },
        ),
        migrations.AddField(
            model_name='role',
            name='role_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Role_Type'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='relationship_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Relationship_Type'),
        ),
        migrations.AddField(
            model_name='post_code',
            name='ward',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Ward'),
        ),
        migrations.AddField(
            model_name='person',
            name='addresses',
            field=models.ManyToManyField(through='people.Residence', to='people.Address'),
        ),
        migrations.AddField(
            model_name='person',
            name='answers',
            field=models.ManyToManyField(through='people.Answer', to='people.Option'),
        ),
        migrations.AddField(
            model_name='person',
            name='capture_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Capture_Type'),
        ),
        migrations.AddField(
            model_name='person',
            name='children_centres',
            field=models.ManyToManyField(through='people.CC_Registration', to='people.Children_Centre'),
        ),
        migrations.AddField(
            model_name='person',
            name='default_role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Role_Type'),
        ),
        migrations.AddField(
            model_name='person',
            name='ethnicity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Ethnicity'),
        ),
        migrations.AddField(
            model_name='person',
            name='events',
            field=models.ManyToManyField(through='people.Event_Registration', to='people.Event'),
        ),
        migrations.AddField(
            model_name='person',
            name='families',
            field=models.ManyToManyField(blank=True, to='people.Family'),
        ),
        migrations.AddField(
            model_name='person',
            name='relationships',
            field=models.ManyToManyField(through='people.Relationship', to='people.Person'),
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Question'),
        ),
        migrations.AddField(
            model_name='event_registration',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person'),
        ),
        migrations.AddField(
            model_name='event_registration',
            name='role_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Role_Type'),
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Event_Type'),
        ),
        migrations.AddField(
            model_name='cc_registration',
            name='children_centre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Children_Centre'),
        ),
        migrations.AddField(
            model_name='cc_registration',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person'),
        ),
        migrations.AddField(
            model_name='answer',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Option'),
        ),
        migrations.AddField(
            model_name='answer',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Question'),
        ),
        migrations.AddField(
            model_name='address',
            name='post_code',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='people.Post_Code'),
        ),
    ]
