from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import ClientProfile, User


class ClientProfileInline(admin.StackedInline):
    """Allows editing client profile fields directly inside the User admin page."""

    model = ClientProfile
    can_delete = False
    verbose_name_plural = "Client Profile Details"
    fk_name = "user"
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ClientProfileInline, )

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


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    """Standalone admin registration for direct ClientProfile management."""

    list_display = (
        "user",
        "country",
        "preferred_currency",
        "is_international",
        "created_at",
    )
    list_filter = ("preferred_currency", "is_international", "country")
    search_fields = ("user__username", "user__email", "tax_id", "company_name")
