# Generated by Django 2.1 on 2019-02-28 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_userdata_fb_profile_image_large'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebookevent',
            name='end_time',
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]
