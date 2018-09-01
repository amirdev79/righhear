# Generated by Django 2.1 on 2018-08-30 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=0, editable=False, max_digits=9),
        ),
        migrations.AddField(
            model_name='venue',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=0, editable=False, max_digits=9),
        ),
    ]