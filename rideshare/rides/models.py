from django.db import models
from utils.model_abstract import Model
from authentication.models import Profile
from utils.choices import RIDE_STATUS

# Create your models here.


class Rides(Model):
    rider = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name='rider')
    driver = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='driver')
    pickup_location = models.CharField(max_length=255, blank=True, null=True)
    dropoff_location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, choices=RIDE_STATUS, blank=True, null=True)
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    current_location_address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)