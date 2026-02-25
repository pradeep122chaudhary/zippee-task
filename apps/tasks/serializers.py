from __future__ import annotations

from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "user_name",
            "title",
            "description",
            "completed",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user_name", "created_at", "updated_at")

    def get_user_name(self, obj) -> str:
        full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        if full_name:
            return full_name
        return obj.user.email

    def validate_title(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Title cannot be blank.")
        return cleaned
