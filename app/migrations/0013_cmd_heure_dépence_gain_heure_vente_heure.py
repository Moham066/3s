# Generated by Django 4.2.10 on 2024-04-04 22:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_cmd_dépence_gain_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='cmd',
            name='heure',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='dépence_gain',
            name='heure',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='vente',
            name='heure',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
