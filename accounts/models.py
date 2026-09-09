from typing import TYPE_CHECKING, Any
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models
from utils.validators import validate_not_disposable_email

if TYPE_CHECKING:
    _BaseUserManager = DjangoUserManager["User"]
else:
    _BaseUserManager = DjangoUserManager


class UserManager(_BaseUserManager):
    """Custom manager for User model with typed user creation and role assignments."""

    def create_user(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("role", User.Role.CLIENT)
        if email:
            email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model providing user roles and simple contact details."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff/Engineer"
        CLIENT = "CLIENT", "Client/Customer"

    email = models.EmailField(
        unique=True,
        validators=[validate_not_disposable_email],
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)

    objects: UserManager = UserManager()

    def is_client(self) -> bool:
        return self.role == self.Role.CLIENT

    def is_staff_member(self) -> bool:
        return self.role in [self.Role.STAFF, self.Role.ADMIN]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.STAFF:
            self.is_staff = True
            self.is_superuser = False
        elif self.role == self.Role.CLIENT:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)
