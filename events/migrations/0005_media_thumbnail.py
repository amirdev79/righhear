# Generated by Django 2.1 on 2018-09-01 13:29

from django.db import migrations, models
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_event_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to=events.models.Media.thumbnail_media_path),
        ),
    ]