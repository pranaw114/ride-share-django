# tasks.py
from celery import shared_task
import time
from .models import Rides

@shared_task
def simulate_ride_movement(ride_id):
    ride = Rides.objects.get(id=ride_id)
    steps = 5  # simulate 5 updates
    lat, lon = ride.current_latitude, ride.current_longitude

    for _ in range(steps):
        # Simulate a slight move
        lat += 0.0001
        lon += 0.0001
        ride.current_latitude = lat
        ride.current_longitude = lon

        ride.save()

        time.sleep(5)  # Simulate time between location updates
