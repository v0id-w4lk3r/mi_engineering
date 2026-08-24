from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff/Engineer"
        CLIENT = "CLIENT", "Client/Customer"

    role = models.CharField(max_length=20,
                            choices=Role.choices,
                            default=Role.CLIENT)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def is_client(self):
        return self.role == self.Role.CLIENT

    def is_staff_member(self):
        return self.role in [self.Role.STAFF, self.Role.ADMIN]

    def save(self, *args, **kwargs):
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
