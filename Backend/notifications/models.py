from django.db import models


# Create your models here.

class NotificationPlatform(models.Model):
    notification_platform_id = models.AutoField(primary_key=True)
    notification_platform_name = models.CharField(max_length=100)
    notification_platform_configuration = models.JSONField()
