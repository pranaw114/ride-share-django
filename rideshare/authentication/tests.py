from django.test import TestCase
from .models import Profile
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse


# Create your tests here.


class ProfileModelTest(TestCase):
    def setUp(self):
        # Create a User
        self.user = User.objects.create_user(
            username="johndoe",
            email="john@example.com",
            password="Password123!"
        )
        # Create a Profile linked to that User
        self.profile = Profile.objects.create(
            user=self.user,
            full_name="John Doe",
            phone_number="1234567890",
            user_type="driver",
            latitude=12.9716,
            longitude=77.5946,
            is_active=True
        )

    def test_profile_creation(self):
        """Profile is correctly created and linked to User."""
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.full_name, "John Doe")
        self.assertEqual(self.profile.phone_number, "1234567890")
        self.assertEqual(self.profile.user_type, "driver")
        self.assertTrue(self.profile.is_active)

    def test_latitude_longitude_fields(self):
        """Latitude and longitude fields store floats correctly."""
        self.assertIsInstance(self.profile.latitude, float)
        self.assertIsInstance(self.profile.longitude, float)
        self.assertAlmostEqual(self.profile.latitude, 12.9716, places=4)
        self.assertAlmostEqual(self.profile.longitude, 77.5946, places=4)


class UserModelTest(TestCase):
    def test_user_creation(self):
        """Ensure User creation works as expected."""
        user = User.objects.create_user(
            username="janedoe",
            email="jane@example.com",
            password="SecurePass1!"
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "janedoe")
        self.assertEqual(user.email, "jane@example.com")
        # Password is hashed; check authentication:
        self.assertTrue(user.check_password("SecurePass1!"))


class RegistrationAPITest(APITestCase):
    def setUp(self):
        self.url = reverse('register')
        self.valid_payload = {
            "email": "testuser@example.com",
            "password": "Test@1234",
            "confirm_password": "Test@1234",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "1234567890",
            "full_name": "John Doe",
            "user_type": "Rider",
        }

    def test_register_creates_user_and_profile(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify User and Profile are created
        user = User.objects.filter(email=self.valid_payload["email"]).first()
        self.assertIsNotNone(user)

        profile = Profile.objects.filter(user=user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.phone_number, self.valid_payload["phone_number"])
        self.assertEqual(profile.full_name, self.valid_payload["full_name"])

    def test_register_email_unique(self):
        self.client.post(self.url, self.valid_payload, format='json')
        payload = self.valid_payload.copy()
        payload["phone_number"] = "0987654321"  # new phone
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json()["errors"])

    def test_register_password_mismatch(self):
        payload = self.valid_payload.copy()
        payload["confirm_password"] = "WrongPass123!"
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirm_password", response.json()["errors"])

    def test_register_phone_number_unique(self):
        self.client.post(self.url, self.valid_payload, format='json')
        payload = self.valid_payload.copy()
        payload["email"] = "newemail@example.com"
        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.json()["errors"])