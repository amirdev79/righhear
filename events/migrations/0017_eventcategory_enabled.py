# Generated by Django 2.1 on 2019-02-03 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_eventsubcategory_title_heb'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventcategory',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
