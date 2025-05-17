from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Rides
from .serializers import RideSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, APIException
from utils.constants import REQUESTED
from utils.helpers import success_response, error_response, update_location, find_nearest_driver
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.


class RidesViewSet(ModelViewSet): # create ride request
    queryset = Rides.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        profile = self.request.user.profile

        if profile.user_type != 'Rider':
            raise PermissionDenied("Only rider users may request rides.")

        serializer.save(
            rider=profile,
            status=REQUESTED
        )
        

class RidesListViewSet(ModelViewSet): # list all rides
    queryset = Rides.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def list_rides(self, request):
        rides = self.get_queryset()

        serializer = self.get_serializer(rides, many=True)
        return success_response(
            serializer.data
        )
    

class RidesDetailsViewSet(ModelViewSet): # ride details
    queryset = Rides.objects.all()
    serializer_class = RideSerializer


class UpdateRidesStatusViewSet(ModelViewSet):
    queryset = Rides.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        try:
            ride = self.get_object()
            user_profile = request.user.profile

            if ride.driver != user_profile:
                return error_response(
                    error_message = "Only the driver can update the ride status.",
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = self.get_serializer(ride, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return success_response(
                    serializer.data,)
            return error_response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return error_response("Something went wrong.")
        

class RideLocationUpdateView(APIView):
    def post(self, request):
        ride_id = request.data.get('ride_id')
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        update_location(ride_id, float(lat), float(lon))
        return success_response(success_message='Location updated')


class FindNearestDriverView(APIView): # find the nearest driver
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            ride_id = request.data.get("ride_id")
            ride = Rides.objects.active().get(id=ride_id)

            if ride.status != 'Requested':
                return error_response(
                    error_message="Ride must be in 'Requested' status to assign.",
                    status=status.HTTP_400_BAD_REQUEST
                )

            driver = find_nearest_driver(ride.pickup_location)
            if not driver:
                return error_response(
                    error_message="No available drivers within radius.",
                    status=status.HTTP_404_NOT_FOUND
                )

            ride.driver = driver
            ride.save()
            driver.save()

            return success_response(
                RideSerializer(ride).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response("Something went wrong.")
        

class AcceptRideViewSet(ModelViewSet):
    queryset = Rides.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    # @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        try:
            ride = self.get_object()
            driver_profile = request.user.profile

            # Only drivers can accept rides
            if driver_profile.user_type != 'Driver':
                return error_response(
                    error_message= 'Only drivers may accept rides.',
                    status=status.HTTP_403_FORBIDDEN
                )

            # Ride must be in 'requested' status
            if ride.status != 'Requested':
                return Response(
                    {'detail': 'Ride must be requested to be accepted.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Assign this driver and update status
            ride.driver = driver_profile
            ride.status = 'Accepted'
            ride.save()

            # Mark driver unavailable (optional)
            # driver_profile.is_available = False
            # driver_profile.save()

            return success_response(
                RideSerializer(ride).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response("Something went wrong.")