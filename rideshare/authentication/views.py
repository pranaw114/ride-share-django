from django.shortcuts import render
from .serializers import UserSerializer, ProfileSerializer, LoginSerializer
from django.db import transaction
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from utils.helpers import success_response,error_response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth import login, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.


class UserRegistrationViewSet(ViewSet):

    def create(self, request):
        try:
            with transaction.atomic():
                user_serializer = UserSerializer(data=request.data)
                profile_serializer = ProfileSerializer(data=request.data)

                user_is_valid = user_serializer.is_valid()
                profile_is_valid = profile_serializer.is_valid()

                if user_is_valid and profile_is_valid:
                    user_instance = user_serializer.save(
                        username=user_serializer.validated_data["email"]
                    )
                    profile_instance = profile_serializer.save(
                        user_id=user_instance.id,
                    )

                    return success_response(
                        ProfileSerializer(profile_instance).data,
                        status=status.HTTP_201_CREATED,
                    )

                combined_errors = {}
                if not user_is_valid:
                    combined_errors.update(user_serializer.errors)
                if not profile_is_valid:
                    combined_errors.update(profile_serializer.errors)

                return error_response(
                    error_message="error",
                    errors=combined_errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return error_response(
                error_message="Something went wrong!",
            )
        

class Lognin(APIView):

    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')
            user = authenticate(username=username, password=password)
            if user is None or (user and not user.is_active):
                return error_response(
                    error_message='Invalid credentials.',
                    status=status.HTTP_400_BAD_REQUEST
                )
    
            profile = user.profile
            if not profile:
                return error_response(
                    errors={'username': ['Inavlid Username.']}, status=status.HTTP_400_BAD_REQUEST)
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return success_response({'access': str(access_token),'refresh': str(refresh)},
                                        status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(
                error_message="Something went wrong!"
            )