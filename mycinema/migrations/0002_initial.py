# Generated by Django 4.1.7 on 2023-04-06 20:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mycinema', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='seance',
            name='film',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mycinema.film'),
        ),
        migrations.AddField(
            model_name='seance',
            name='hall',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mycinema.hall'),
        ),
        migrations.AlterUniqueTogether(
            name='film',
            unique_together={('title', 'release_date')},
        ),
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together={('seat', 'row', 'seance')},
        ),
    ]