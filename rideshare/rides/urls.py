from django.urls import path
from .views import (
    RidesViewSet,
    RidesListViewSet,
    RidesDetailsViewSet,
    UpdateRidesStatusViewSet,
    RideLocationUpdateView,
    FindNearestDriverView,
    AcceptRideViewSet,
)


urlpatterns = [
    path('create-ride-request', RidesViewSet.as_view({'post': 'create'}), name="create-ride-request"),
    path('list-rides', RidesListViewSet.as_view({'get': 'list'}), name="list-rides"),
    path('ride-details/<int:pk>', RidesDetailsViewSet.as_view({'get': 'retrieve'}), name="ride-details"),
    path('update-ride-status/<int:pk>', UpdateRidesStatusViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name="update-ride-status"),
    path('update-location', RideLocationUpdateView.as_view(), name="update-location"),
    path('find-driver', FindNearestDriverView.as_view(), name="find-driver"),
    path('accept-ride/<int:pk>', AcceptRideViewSet.as_view({'post': 'accept'}), name="accept-ride"),
]