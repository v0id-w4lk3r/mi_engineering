from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "company_name",
        "is_staff",
    )

    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "company_name",
    )

    # Convert parent add_fieldsets tuple/list safely and ensure fields is a list
    add_fieldsets = list(BaseUserAdmin.add_fieldsets or ()) + [
        (
            "Custom Profile Info",
            {
                "fields": ["role", "company_name", "phone_number"],
            },
        ),
    ]

    def get_fieldsets(self, request: Any, obj: Any = None) -> Any:
        fieldsets = list(super().get_fieldsets(request, obj))
        custom_fieldset = (
            "Custom Profile Info",
            {
                "fields": ("role", "company_name", "phone_number"),
            },
        )
        return fieldsets + [custom_fieldset]
