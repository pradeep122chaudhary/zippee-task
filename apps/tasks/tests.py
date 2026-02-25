from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import UserType

from .models import Task


User = get_user_model()


class TaskAPITests(APITestCase):

    def setUp(self) -> None:
        self.password = "StrongPass123!"
        user_role = UserType.objects.get(code=UserType.USER)
        admin_role = UserType.objects.get(code=UserType.ADMIN)
        super_admin_role = UserType.objects.get(code=UserType.SUPER_ADMIN)
        self.user = User.objects.create_user(
            email="owner@example.com",
            password=self.password,
            user_type=user_role,
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password=self.password,
            user_type=user_role,
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password=self.password,
            user_type=admin_role,
        )
        self.super_admin_user = User.objects.create_user(
            email="superadmin@example.com",
            password=self.password,
            user_type=super_admin_role,
        )

        self.user_task = Task.objects.create(
            user=self.user,
            title="Owner Task",
            description="Task owned by the authenticated user",
            completed=False,
        )
        self.other_task = Task.objects.create(
            user=self.other_user,
            title="Other User Task",
            description="Task owned by another user",
            completed=True,
        )
        self.list_url = reverse("v1:task-list-create")
        self.detail_url = reverse("v1:task-detail", kwargs={"task_id": self.user_task.id})

    def test_create_task(self) -> None:
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "Write API docs",
            "description": "Document endpoints and examples",
            "completed": False,
        }
        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["task"]["title"], payload["title"])
        self.assertTrue(Task.objects.filter(user=self.user, title=payload["title"]).exists())

    def test_get_task_list(self) -> None:
        Task.objects.create(user=self.user, title="Second Owner Task", completed=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)

    def test_retrieve_single_task(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user_task.id)
        self.assertIn("user_name", response.data)
        self.assertNotIn("user", response.data)

    def test_update_task(self) -> None:
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "Updated Owner Task",
            "description": "Updated description",
            "completed": True,
        }
        response = self.client.put(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_task.refresh_from_db()
        self.assertEqual(self.user_task.title, payload["title"])
        self.assertTrue(self.user_task.completed)

    def test_delete_task(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.user_task.id).exists())

    def test_permission_another_user_cannot_modify_task(self) -> None:
        self.client.force_authenticate(user=self.other_user)
        payload = {
            "title": "Illegal Update",
            "description": "Should not pass",
            "completed": False,
        }
        update_response = self.client.put(self.detail_url, payload, format="json")
        delete_response = self.client.delete(self.detail_url, format="json")

        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_task(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            "title": "Admin Updated Task",
            "description": "Changed by admin",
            "completed": True,
        }
        response = self.client.put(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_task.refresh_from_db()
        self.assertEqual(self.user_task.title, "Admin Updated Task")

    def test_admin_can_get_any_task(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        other_detail_url = reverse("v1:task-detail", kwargs={"task_id": self.other_task.id})
        response = self.client.get(other_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.other_task.id)

    def test_admin_can_delete_any_task(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        other_detail_url = reverse("v1:task-detail", kwargs={"task_id": self.other_task.id})
        response = self.client.delete(other_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.other_task.id).exists())

    def test_super_admin_can_get_update_delete_any_task(self) -> None:
        self.client.force_authenticate(user=self.super_admin_user)
        other_detail_url = reverse("v1:task-detail", kwargs={"task_id": self.other_task.id})
        get_response = self.client.get(other_detail_url, format="json")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        payload = {
            "title": "Super Admin Updated Task",
            "description": "Updated by super admin",
            "completed": False,
        }
        update_response = self.client.put(other_detail_url, payload, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        delete_response = self.client.delete(other_detail_url, format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_filter_any_user_tasks(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"{self.list_url}?user_id={self.other_user.id}", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.other_task.id)

    def test_filter_tasks_by_completed(self) -> None:
        Task.objects.create(user=self.user, title="Done Task", completed=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.list_url}?completed=true", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(response.data["results"][0]["completed"])

    def test_search_tasks_by_title(self) -> None:
        Task.objects.create(user=self.user, title="Buy groceries", completed=False)
        Task.objects.create(user=self.user, title="Plan sprint", completed=False)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.list_url}?search=groc", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Buy groceries")

    def test_pagination_returns_expected_shape(self) -> None:
        for index in range(15):
            Task.objects.create(user=self.user, title=f"Task {index}", completed=False)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)
