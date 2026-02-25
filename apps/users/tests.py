from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import UserType

User = get_user_model()


class AuthAPITests(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse("v1:register")
        self.login_url = reverse("v1:login")
        self.token_url = reverse("v1:token_obtain_pair")
        self.user_data_url = reverse("v1:user-data")
        self.valid_password = "StrongPass123!"
        self.user_payload = {
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Doe",
            "password": self.valid_password,
            "password_confirm": self.valid_password,
        }

    def test_register_user(self) -> None:
        response = self.client.post(self.register_url, self.user_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User registered successfully.")
        self.assertTrue(User.objects.filter(email="alice@example.com").exists())
        user = User.objects.get(email="alice@example.com")
        self.assertTrue(user.check_password(self.valid_password))
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Doe")
        self.assertIsNotNone(user.user_type)
        self.assertEqual(user.user_type.code, UserType.USER)

    def test_register_requires_first_and_last_name(self) -> None:
        payload = {
            "email": "missing-name@example.com",
            "password": self.valid_password,
            "password_confirm": self.valid_password,
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)

    def test_user_type_seed_data_exists(self) -> None:
        role_codes = set(UserType.objects.values_list("code", flat=True))
        self.assertSetEqual(
            role_codes,
            {
                UserType.USER,
                UserType.STAFF,
                UserType.ADMIN,
                UserType.SUPER_ADMIN,
            },
        )

    def test_super_admin_user_type_sets_permission_flags(self) -> None:
        super_admin_type = UserType.objects.get(code=UserType.SUPER_ADMIN)
        user = User.objects.create_user(
            email="root-role@example.com",
            password=self.valid_password,
            user_type=super_admin_type,
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_login_user_with_email(self) -> None:
        User.objects.create_user(
            email="bob@example.com",
            password=self.valid_password,
            first_name="Bob",
            last_name="Stone",
        )
        response = self.client.post(
            self.login_url,
            {"email": "bob@example.com", "password": self.valid_password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_generation_with_email(self) -> None:
        User.objects.create_user(
            email="charlie@example.com",
            password=self.valid_password,
            first_name="Charlie",
            last_name="Ray",
        )
        response = self.client.post(
            self.token_url,
            {"email": "charlie@example.com", "password": self.valid_password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_regular_user_sees_only_own_data(self) -> None:
        user_role = UserType.objects.get(code=UserType.USER)
        current_user = User.objects.create_user(
            email="user-one@example.com",
            password=self.valid_password,
            user_type=user_role,
            first_name="User",
            last_name="One",
        )
        User.objects.create_user(
            email="user-two@example.com",
            password=self.valid_password,
            user_type=user_role,
            first_name="User",
            last_name="Two",
        )
        self.client.force_authenticate(user=current_user)
        response = self.client.get(self.user_data_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["email"], "user-one@example.com")

    def test_admin_and_super_admin_see_all_user_data(self) -> None:
        user_role = UserType.objects.get(code=UserType.USER)
        admin_role = UserType.objects.get(code=UserType.ADMIN)
        super_admin_role = UserType.objects.get(code=UserType.SUPER_ADMIN)
        User.objects.create_user(
            email="normal-one@example.com",
            password=self.valid_password,
            user_type=user_role,
            first_name="Normal",
            last_name="One",
        )
        User.objects.create_user(
            email="normal-two@example.com",
            password=self.valid_password,
            user_type=user_role,
            first_name="Normal",
            last_name="Two",
        )
        admin_user = User.objects.create_user(
            email="admin-data@example.com",
            password=self.valid_password,
            user_type=admin_role,
            first_name="Admin",
            last_name="Data",
        )
        super_admin_user = User.objects.create_user(
            email="super-data@example.com",
            password=self.valid_password,
            user_type=super_admin_role,
            first_name="Super",
            last_name="Data",
        )
        self.client.force_authenticate(user=admin_user)
        admin_response = self.client.get(self.user_data_url, format="json")
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(admin_response.data["count"], 4)
        self.client.force_authenticate(user=super_admin_user)
        super_response = self.client.get(self.user_data_url, format="json")
        self.assertEqual(super_response.status_code, status.HTTP_200_OK)
        self.assertEqual(super_response.data["count"], admin_response.data["count"])

    def test_login_with_invalid_credentials_returns_401(self) -> None:
        User.objects.create_user(
            email="invalid-auth@example.com",
            password=self.valid_password,
            first_name="Invalid",
            last_name="Auth",
        )
        response = self.client.post(
            self.login_url,
            {"email": "invalid-auth@example.com", "password": "WrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
