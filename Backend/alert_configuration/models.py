from django.db import models
from django.contrib.auth.models import User
from ripe_atlas.models import Measurement
# Create your models here.


class AlertConfiguration(models.Model):
    alert_configuration_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    alert_configuration_type = models.CharField(max_length=100)
    alert_configuration = models.JSONField()

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['user', 'measurement', 'alert_configuration_type'],
    #                                 name='unique_user_alert_configuration_on_measurement')
    #     ]


class Alert(models.Model):
    class Severity(models.TextChoices):
        WARNING = 'Warning'
        MINOR = 'Minor'
        MAJOR = 'Major'
        CRITICAL = 'Critical'

    alert_id = models.AutoField(primary_key=True)
    alert_configuration = models.ForeignKey(AlertConfiguration, on_delete=models.CASCADE)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.CRITICAL)
    description = models.TextField()
    feedback = models.BooleanField(null=True)