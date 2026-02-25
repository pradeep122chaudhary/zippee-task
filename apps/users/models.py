from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserType(models.Model):

    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

    ROLE_CHOICES = (
        (USER, "User"),
        (STAFF, "Staff"),
        (ADMIN, "Admin"),
        (SUPER_ADMIN, "Super Admin"),
    )

    code = models.CharField(max_length=32, choices=ROLE_CHOICES, unique=True)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True)
    user_type = models.ForeignKey(
        UserType,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def has_global_data_access(self) -> bool:
        if self.is_superuser:
            return True
        if self.is_staff:
            return True
        if not self.user_type_id:
            return False
        return self.user_type.code in {UserType.ADMIN, UserType.SUPER_ADMIN}

    def apply_user_type_flags(self) -> None:
        if not self.user_type_id:
            return

        user_type_code = self.user_type.code
        if user_type_code == UserType.SUPER_ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif user_type_code in {UserType.ADMIN, UserType.STAFF}:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False

    def save(self, *args, **kwargs):
        self.apply_user_type_flags()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
