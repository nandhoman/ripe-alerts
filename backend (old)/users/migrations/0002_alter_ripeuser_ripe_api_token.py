# Generated by Django 3.2.8 on 2022-01-27 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ripeuser',
            name='ripe_api_token',
            field=models.UUIDField(null=True),
        ),
    ]