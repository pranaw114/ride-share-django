from rest_framework import serializers
from django.contrib.auth.models import User
from authentication.models import Profile
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator
import re
from django.contrib.auth.hashers import make_password


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

    full_name = serializers.CharField(
        min_length=2,
        max_length=100,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z\s]+$",
                message="This field can only contain letters",
            ),
        ],
    )

    phone_number = serializers.CharField(
        min_length=10,
        max_length=10,
        required=True,
        validators=[
            RegexValidator(regex=r"^[0-9]*$", message="This field can only contain numbers."),
            UniqueValidator(
                queryset=Profile.objects.all(), message="Phone number is already registered"
            ),
        ],
    )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = User
        fields = "__all__"

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Email is already registered"
            ),
        ]
    )

    def validate(self, data):
        """
        Check the password and confirm_password are the same.
        """
        password = data.get("password")
        confirm_password = self.initial_data.get(
            "confirm_password"
        )

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Password and confirm password do not match."}
            )
        
        if len(password) < 8:
            raise serializers.ValidationError(
                {"password": "Password must be at least 8 characters long."}
            )
        
        if not re.search(r"[A-Z]", password):
            raise serializers.ValidationError(
                {"password": "Password must contain at least one uppercase letter."}
            )
        
        if not re.search(r"[a-z]", password):
            raise serializers.ValidationError(
                {"password": "Password must contain at least one lowercase letter."}
            )
        
        if not re.search(r"\d", password):
            raise serializers.ValidationError(
                {"password": "Password must contain at least one digit."}
            )
        
        if not re.search(r"[^\w\s]", password):
            raise serializers.ValidationError(
                {"password": ("Password must contain at least one special character.")}
            )

        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        validated_data["username"] = validated_data["email"]
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)