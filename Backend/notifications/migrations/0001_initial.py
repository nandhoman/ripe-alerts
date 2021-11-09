# Generated by Django 3.2.8 on 2021-11-05 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationPlatform',
            fields=[
                ('notification_platform_id', models.AutoField(primary_key=True, serialize=False)),
                ('notification_platform_name', models.CharField(max_length=100)),
                ('notification_platform_configuration', models.JSONField()),
            ],
        ),
    ]