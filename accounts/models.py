from typing import TYPE_CHECKING, Any
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.validators import validate_not_disposable_email

if TYPE_CHECKING:
    _BaseUserManager = DjangoUserManager["User"]
else:
    _BaseUserManager = DjangoUserManager


class UserManager(_BaseUserManager):
    """Custom manager for User model with typed user creation and role assignments."""

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.CLIENT)
        if email:
            email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,
                         username,
                         email=None,
                         password=None,
                         **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff/Engineer"
        CLIENT = "CLIENT", "Client/Customer"

    email = models.EmailField(unique=True,
                              validators=[validate_not_disposable_email])
    role = models.CharField(max_length=20,
                            choices=Role.choices,
                            default=Role.CLIENT)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    objects: UserManager = UserManager()

    def is_client(self) -> bool:
        return self.role == self.Role.CLIENT

    def is_staff_member(self) -> bool:
        return self.role in [self.Role.STAFF, self.Role.ADMIN]

    def save(self, *args, **kwargs):
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.STAFF:
            self.is_staff = True
            self.is_superuser = False
        elif self.role == self.Role.CLIENT:
            if not (self.is_superuser or self.is_staff):
                self.is_staff = False
                self.is_superuser = False

        super().save(*args, **kwargs)


class ClientProfile(models.Model):
    """Profile model storing detailed business and operational attributes for client accounts."""

    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name="client_profile")
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="GST, VAT, or Tax Identification Number")
    billing_address = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default="India")

    # Additional Industry Context
    industry_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=
        "e.g. Automotive, Aerospace, Precision Machining, Construction")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Client Profile - {self.user.get_full_name() or self.user.username}"


# --- SIGNALS ---
@receiver(post_save, sender=User)
def create_or_update_client_profile(sender: type, instance: User,
                                    created: bool, **kwargs: Any) -> None:
    """Automatically creates a ClientProfile whenever a User with the CLIENT role is created."""
    if instance.role == User.Role.CLIENT:
        ClientProfile.objects.get_or_create(user=instance)
