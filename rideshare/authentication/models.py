from django.db import models
from django.contrib.auth.models import User
from utils.model_abstract import Model
from utils.choices import USER_TYPES

# Create your models here.


class Profile(Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    full_name = models.CharField(max_length=40, blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    user_type = models.CharField(max_length=150, choices=USER_TYPES, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)

    def __str__(self):
        return self.full_name