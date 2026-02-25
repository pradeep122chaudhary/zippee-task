from __future__ import annotations

import re

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.SlugRelatedField(read_only=True, slug_field="code")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
            "date_of_birth",
            "bio",
            "address",
            "city",
            "country",
            "is_staff",
        )
        read_only_fields = ("id", "is_staff")


class RegisterSerializer(serializers.ModelSerializer):
    user_type = serializers.SlugRelatedField(
        slug_field="code",
        queryset=UserType.objects.all(),
        required=False,
        allow_null=True,
    )
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
            "date_of_birth",
            "bio",
            "address",
            "city",
            "country",
            "password",
            "password_confirm",
        )

    def validate_email(self, value: str) -> str:
        normalized_email = value.strip().lower()
        if User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized_email

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def validate_user_type(self, value: UserType | None) -> UserType | None:
        if value and value.code != UserType.USER:
            raise serializers.ValidationError(
                "You can only register with the 'user' role. Privileged roles require admin action."
            )
        return value

    def validate_phone_number(self, value: str) -> str:
        cleaned = value.strip()
        if cleaned and not re.fullmatch(r"[0-9+\-\s()]+", cleaned):
            raise serializers.ValidationError(
                "Phone number may contain digits, spaces, and + - ( ) symbols only."
            )
        return cleaned

    def create(self, validated_data: dict) -> User:
        validated_data.pop("password_confirm")
        user_type = validated_data.pop("user_type", None)
        if user_type is None:
            user_type = UserType.objects.filter(code=UserType.USER).first()
        if user_type:
            validated_data["user_type"] = user_type
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs: dict) -> dict:
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password")
        request = self.context.get("request")
        user = authenticate(request=request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationFailed("This account is disabled.")
        attrs["user"] = user
        return attrs


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD
