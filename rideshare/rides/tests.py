from django.test import TestCase
from django.contrib.auth.models import User
from rides.models import Rides, Profile
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
import json
from unittest.mock import patch


class RidesModelTest(TestCase):
    def setUp(self):
        self.rider_user = User.objects.create_user(username="rider1", password="pass123")
        self.driver_user = User.objects.create_user(username="driver1", password="pass456")
        self.rider_profile = Profile.objects.create(user=self.rider_user, full_name="Rider One")
        self.driver_profile = Profile.objects.create(user=self.driver_user, full_name="Driver One")
        self.list_url = reverse('list-rides') 

    def test_create_ride(self):
        ride = Rides.objects.create(
            rider=self.rider_profile,
            driver=self.driver_profile,
            pickup_location="Location A",
            dropoff_location="Location B",
            status="requested",
            current_latitude=12.9716,
            current_longitude=77.5946,
            current_location_address="Some street, City",
            is_active=True
        )

        self.assertEqual(ride.rider, self.rider_profile)
        self.assertEqual(ride.driver, self.driver_profile)
        self.assertEqual(ride.pickup_location, "Location A")
        self.assertEqual(ride.dropoff_location, "Location B")
        self.assertEqual(ride.status, "requested")
        self.assertEqual(ride.current_latitude, 12.9716)
        self.assertEqual(ride.current_longitude, 77.5946)
        self.assertEqual(ride.current_location_address, "Some street, City")
        self.assertTrue(ride.is_active)

    def test_default_is_active(self):
        ride = Rides.objects.create(
            rider=self.rider_profile,
            driver=self.driver_profile
        )
        self.assertTrue(ride.is_active)


class RidesViewSetTest(APITestCase):

    def setUp(self):
        # Create a Rider user and profile
        self.rider_user = User.objects.create_user(username="rideruser", email="rider@example.com", password="Passw0rd!")
        self.rider_profile = Profile.objects.create(user=self.rider_user, user_type="Rider", phone_number="1234567890", full_name="Rider")
        
        # Create a non-rider user and profile
        self.non_rider_user = User.objects.create_user(username="driveruser", email="driver@example.com", password="Passw0rd!")
        self.non_rider_profile = Profile.objects.create(user=self.non_rider_user, user_type="Driver", phone_number="0987654321", full_name="Driver")
        
        self.client = APIClient()
        self.url = reverse('create-ride-request')

    def test_rider_can_create_ride(self):
        self.client.force_authenticate(user=self.rider_user)
        payload = {
            "pickup_location": "123 Main St",
            "dropoff_location": "456 Elm St",
        }
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rides.objects.count(), 1)
        ride = Rides.objects.first()
        self.assertEqual(ride.rider, self.rider_profile)
        self.assertEqual(ride.status, 'Requested')

    def test_non_rider_cannot_create_ride(self):
        self.client.force_authenticate(user=self.non_rider_user)
        payload = {
            "pickup_location": "123 Main St",
            "dropoff_location": "456 Elm St",
        }
        response = self.client.post(self.url, payload, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Only rider users may request rides.", response.data.get("message", "") or response.content.decode())
        self.assertEqual(Rides.objects.count(), 0)

    def test_list_all_rides(self):
        # Arrange: create some rides
        Rides.objects.create(
            rider=self.rider_profile,
            pickup_location="A",
            dropoff_location="B",
            status="Requested"
        )
        Rides.objects.create(
            rider=self.rider_profile,
            pickup_location="X",
            dropoff_location="Y",
            status="Requested"
        )

        # Act
        self.client.force_authenticate(self.rider_user)
        url = reverse('list-rides')
        resp = self.client.get(url, format='json')

        # Assert
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        # If wrapped under 'data', unwrap; otherwise use directly
        if isinstance(data, dict) and 'data' in data:
            rides = data['data']
        else:
            rides = data

        self.assertIsInstance(rides, list)
        self.assertGreaterEqual(len(rides), 2)

    def test_retrieve_ride_detail(self):
        # Create user and profile
        user = User.objects.create_user(username='rider', password='Passw0rd!')
        profile = Profile.objects.create(user=user, user_type='Rider', phone_number='1234567890', full_name='Rider')

        # Create a ride linked to profile
        ride = Rides.objects.create(
            rider=profile,
            pickup_location='123 Main St',
            dropoff_location='456 Elm St',
            status='Requested'
        )

        # Authenticate client
        self.client.force_authenticate(user=user)

        url = reverse('ride-details', kwargs={'pk': ride.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], ride.id)
        self.assertEqual(response.data['pickup_location'], ride.pickup_location)
        self.assertEqual(response.data['dropoff_location'], ride.dropoff_location)
        self.assertEqual(response.data['status'], ride.status)


class UpdateRidesStatusViewSetTest(APITestCase):

    def setUp(self):
        # Create driver user and profile
        self.driver_user = User.objects.create_user(username='driveruser', password='Passw0rd!')
        self.driver_profile = Profile.objects.create(user=self.driver_user, user_type='Driver', phone_number='1112223333', full_name='Driver')

        # Create another user who is not the driver
        self.other_user = User.objects.create_user(username='otheruser', password='Passw0rd!')
        self.other_profile = Profile.objects.create(user=self.other_user, user_type='Driver', phone_number='4445556666', full_name='Other')

        # Create a ride assigned to driver_profile
        self.ride = Rides.objects.create(
            rider=None,  # or some rider profile if required
            driver=self.driver_profile,
            pickup_location='123 Main St',
            dropoff_location='456 Elm St',
            status='Requested'
        )

        self.url = reverse('update-ride-status', kwargs={'pk': self.ride.pk})

    def test_driver_can_update_status(self):
        self.client.force_authenticate(user=self.driver_user)
        payload = {'status': 'Accepted'}
        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, 'Accepted')

    def test_non_driver_cannot_update_status(self):
        self.client.force_authenticate(user=self.other_user)
        payload = {'status': 'Accepted'}
        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        content = response.content.decode()
        data = json.loads(content)
        self.assertIn('Only the driver can update the ride status.', data.get('message', ''))


class RideLocationUpdateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user and profile
        self.user = User.objects.create_user(username="rideruser", password="Passw0rd!")
        self.profile = Profile.objects.create(user=self.user, user_type="Rider", phone_number="1234567890", full_name="Rider")

        # Create a ride for that profile
        self.ride = Rides.objects.create(
            rider=self.profile,
            pickup_location="123 Main St",
            dropoff_location="456 Elm St",
            status="Requested",
        )

        self.url = reverse('update-location')

    def test_update_location_success(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "ride_id": self.ride.id,
            "latitude": "12.34567",
            "longitude": "76.54321"
        }

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = json.loads(response.content)
        self.assertIn("Location updated", response_json.get("message", ""))


class FindNearestDriverViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.rider_user = User.objects.create_user("rider", password="pass")
        self.rider_profile = Profile.objects.create(user=self.rider_user, user_type="Driver", latitude=0, longitude=0)
        # Create a ride in Requested status
        self.ride = Rides.objects.create(
            rider=self.rider_profile,
            pickup_location="Somewhere",
            status="Requested"
        )
        self.url = reverse('find-driver')

    def test_no_available_driver_returns_404(self):
        self.client.force_authenticate(self.rider_user)
        response = self.client.post(self.url, {"ride_id": self.ride.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        body = json.loads(response.content)
        self.assertIn("No available drivers", body.get("message", ""))

    def test_find_nearest_driver_ride_not_requested(self):
        self.ride.status = 'InProgress'
        self.ride.save()

        self.client.force_authenticate(user=self.rider_user)
        response = self.client.post(self.url, data={"ride_id": self.ride.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        content = json.loads(response.content.decode())
        self.assertIn("Ride must be in 'Requested' status", content.get('message', '') or '')

    @patch('utils.helpers.find_nearest_driver')
    def test_no_available_driver(self, mock_find_driver):
        mock_find_driver.return_value = None

        self.client.force_authenticate(user=self.rider_user)
        response = self.client.post(self.url, data={"ride_id": self.ride.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        content = json.loads(response.content.decode())
        self.assertIn("No available drivers", content.get('message', '') or '')


class AcceptRideViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Rider user & profile (to create the ride)
        self.rider_user = User.objects.create_user("rider", password="pass")
        self.rider_profile = Profile.objects.create(
            user=self.rider_user,
            user_type="Rider",
            phone_number="1111111111",
            full_name="Rider User"
        )

        # Driver user & profile
        self.driver_user = User.objects.create_user("driver", password="pass")
        self.driver_profile = Profile.objects.create(
            user=self.driver_user,
            user_type="Driver",
            phone_number="2222222222",
            full_name="Driver User"
        )

        # Another non-driver user & profile
        self.other_user = User.objects.create_user("other", password="pass")
        self.other_profile = Profile.objects.create(
            user=self.other_user,
            user_type="Rider",
            phone_number="3333333333",
            full_name="Other User"
        )

        # Ride in Requested status, no driver yet
        self.ride = Rides.objects.create(
            rider=self.rider_profile,
            pickup_location="123 Main St",
            dropoff_location="456 Elm St",
            status="Requested"
        )

        # URL: /accept-ride/<pk>/
        self.url = reverse('accept-ride', kwargs={'pk': self.ride.pk})

    def test_driver_can_accept_ride(self):
        self.client.force_authenticate(self.driver_user)
        response = self.client.post(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride.refresh_from_db()
        # DB assertions
        self.assertEqual(self.ride.driver_id, self.driver_profile.id)
        self.assertEqual(self.ride.status, "Accepted")


    def test_non_driver_cannot_accept_ride(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.post(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        body = json.loads(response.content.decode())
        self.assertIn("Only drivers may accept rides.", body.get('message', ''))