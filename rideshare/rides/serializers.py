from rest_framework import serializers
from .models import Rides


class RideSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rides
        fields = "__all__"