# Generated by Django 5.0.2 on 2024-03-24 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_impression'),
    ]

    operations = [
        migrations.AddField(
            model_name='impression',
            name='code_bar',
            field=models.TextField(default='000000000000'),
        ),
    ]
