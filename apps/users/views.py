from __future__ import annotations

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    EmailTokenObtainPairSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        description="Create a new user account.",
        request=RegisterSerializer,
        examples=[
            OpenApiExample(
                "Register payload",
                value={
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "password": "StrongPass123!",
                    "password_confirm": "StrongPass123!",
                },
                request_only=True,
            )
        ],
        responses={201: UserSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User registered successfully.", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        description="Authenticate user credentials and return access/refresh tokens.",
        request=LoginSerializer,
        examples=[
            OpenApiExample(
                "Login payload",
                value={"email": "john@example.com", "password": "StrongPass123!"},
                request_only=True,
            )
        ],
        responses={200: None},
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class UserDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        description="Regular users get their own data; admin and super admin can view all users.",
        responses={200: UserSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        queryset = User.objects.select_related("user_type").all().order_by("id")
        if not request.user.has_global_data_access():
            queryset = queryset.filter(id=request.user.id)
        serializer = UserSerializer(queryset, many=True)
        return Response(
            {"count": len(serializer.data), "results": serializer.data},
            status=status.HTTP_200_OK,
        )
