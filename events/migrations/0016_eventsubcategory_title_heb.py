# Generated by Django 2.1 on 2019-01-10 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_auto_20190108_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsubcategory',
            name='title_heb',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
