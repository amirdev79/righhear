# Generated by Django 2.1 on 2019-02-07 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_auto_20190203_0946'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]
