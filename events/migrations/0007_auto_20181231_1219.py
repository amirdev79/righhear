# Generated by Django 2.1 on 2018-12-31 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20181120_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(blank=True, db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='venue',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
