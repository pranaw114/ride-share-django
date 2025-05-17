from django.http import JsonResponse
from rest_framework import status
import requests
from rides.models import Rides
from rides.tasks import simulate_ride_movement
from authentication.models import Profile
from utils.constants import DRIVER
from math import radians, cos, sin, sqrt, atan2


def success_response(data=None, success_message="Success", status=status.HTTP_200_OK):
    """Creates a successful JSON response.

    Args:
        data (dict, optional): The data to include in the response. Defaults to None.
        success_message (str, optional): A success message to return. Defaults to "Success".
        status (int, optional): The HTTP status code. Defaults to status.HTTP_200_OK.

    Returns:
        JsonResponse: A JSON response with a success message and optional data.
    """
    response_data = {"message": success_message, "results": {}}
    if data is not None:
        response_data["results"]["data"] = data
    return JsonResponse(response_data, status=status)


def error_response(
    errors={},
    error_message="error",
    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    exception_info=None,
):
    """Creates an error JSON response.

    Args:
        errors (dict, optional): A dictionary of error messages. Defaults to {}.
        error_message (str, optional): A general error message. Defaults to "error".
        status (int, optional): The HTTP status code. Defaults to status.HTTP_500_INTERNAL_SERVER_ERROR.
        exception_info (str, optional): Additional exception information. Defaults to None.

    Returns:
        JsonResponse: A JSON response with the error message, errors, and optional exception info.
    """
    response_data = {
        "message": error_message,
        "errors": errors,
        "exception_info": exception_info,
    }
    return JsonResponse(response_data, status=status)

def update_location(ride_id, lat, lon):
    ride = Rides.objects.get(id=ride_id)
    ride.current_latitude = lat
    ride.current_longitude = lon

    # Get address from Nominatim
    url = 'https://nominatim.openstreetmap.org/reverse'
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json'
    }
    headers = {
        'User-Agent': 'RideShare/1.0 (pranavsuresh114@gmail.com)'  # REQUIRED
    }
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        ride.current_location_address = data.get('display_name')

    ride.save()

    # If status is 'started', simulate movement using Celery
    if ride.status == 'Started':
        simulate_ride_movement.delay(ride_id)


def geocode_location(address):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    response = requests.get(url, params=params, headers={'User-Agent': 'rideshare-app'})
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None, None


def find_nearest_driver(pickup_location, radius_km=5):
    lat, lon = geocode_location(pickup_location)
    if lat is None:
        return None

    candidates = Profile.objects.filter(
        user_type=DRIVER,
        latitude__isnull=False,
        longitude__isnull=False
    )
    nearby = []
    for d in candidates:
        dist = haversine(lat, lon, d.latitude, d.longitude)
        if dist <= radius_km:
            nearby.append((dist, d))
    if not nearby:
        return None

    nearby.sort(key=lambda x: x[0])
    return nearby[0][1]


def haversine(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two points."""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c