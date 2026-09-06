import uuid
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
    """Custom User model providing explicit user roles and custom contact attributes."""

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

    # Type annotation for reverse manager access in Pylance
    addresses: Any

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


class Address(models.Model):
    """Stores multiple delivery/shipping destinations linked directly to a User profile."""

    id: int

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    recipient_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]
        verbose_name_plural = "Addresses"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.recipient_name} - {self.city}, {self.postal_code}"


class ClientProfile(models.Model):
    """Profile model storing detailed operational and tax attributes for client accounts."""

    class Currency(models.TextChoices):
        INR = "INR", "INR (₹)"
        USD = "USD", "USD ($)"
        EUR = "EUR", "EUR (€)"
        GBP = "GBP", "GBP (£)"
        AED = "AED", "AED (د.إ)"
        CAD = "CAD", "CAD ($)"
        AUD = "AUD", "AUD ($)"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="GST, VAT, EIN, TIN, or Business Registration Number",
    )
    preferred_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.USD,
        help_text="Primary currency for invoicing and quotes",
    )
    is_international = models.BooleanField(
        default=False,
        help_text=
        "Flag for cross-border shipping, tax exemptions, or custom billing rules",
    )
    industry_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=
        "e.g. Automotive, Aerospace, Precision Machining, Construction",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        default_address = self.user.addresses.filter(is_default=True).first()
        country_str = f" ({default_address.country})" if default_address else ""
        return f"Client Profile - {self.user.get_full_name() or self.user.username}{country_str}"


# --- SIGNALS ---
@receiver(post_save, sender=User)
def create_or_update_client_profile(sender: type[User], instance: User,
                                    created: bool, **kwargs: Any) -> None:
    if instance.role == User.Role.CLIENT:
        ClientProfile.objects.get_or_create(user=instance)
    else:
        ClientProfile.objects.filter(user=instance).delete()
