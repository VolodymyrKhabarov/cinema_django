# Generated by Django 4.1.7 on 2023-04-06 20:46

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('release_date', models.DateField()),
                ('film_duration', models.DurationField()),
                ('image', models.ImageField(blank=True, upload_to='')),
                ('image_title', models.ImageField(blank=True, upload_to='')),
            ],
            options={
                'db_table': 'Film',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Hall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True)),
                ('row', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('seat', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('is_editable', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'Hall',
            },
        ),
        migrations.CreateModel(
            name='Seance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(validators=[django.core.validators.MinValueValidator(datetime.datetime(2023, 4, 6, 20, 46, 50, 890714, tzinfo=datetime.timezone.utc))])),
                ('finish_time', models.DateTimeField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.datetime(2023, 4, 6, 20, 46, 50, 890714, tzinfo=datetime.timezone.utc))])),
                ('price', models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(0)])),
                ('seats', models.IntegerField()),
                ('is_editable', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'Seance',
                'ordering': ('start_time',),
                'permissions': [('can_edit_seance', 'Can edit seance'), ('can_edit_seance_partially', 'Can partially edit seance'), ('can_view_seance', 'Can view seance'), ('can_view_seance_list', 'Can view seance list')],
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.PositiveIntegerField()),
                ('seat', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('seance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='mycinema.seance')),
            ],
            options={
                'db_table': 'Ticket',
            },
        ),
    ]