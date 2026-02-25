from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserType


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):

    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User
    ordering = ("id",)
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "user_type")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Additional Info",
            {
                "fields": (
                    "user_type",
                    "phone_number",
                    "date_of_birth",
                    "bio",
                    "address",
                    "city",
                    "country",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "user_type",
                ),
            },
        ),
    )
