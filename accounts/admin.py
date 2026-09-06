from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import Address, ClientProfile, User


class ClientProfileInline(admin.StackedInline):
    """Allows editing client profile fields directly inside the User admin page."""

    model = ClientProfile
    can_delete = False
    verbose_name_plural = "Client Profile Details"
    fk_name = "user"
    extra = 0


class AddressInline(admin.TabularInline):
    """Allows managing saved user addresses directly inside the User admin page."""

    model = Address
    extra = 0
    fields = (
        "recipient_name",
        "phone_number",
        "street_address",
        "city",
        "state",
        "postal_code",
        "country",
        "is_default",
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ClientProfileInline, AddressInline)

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
        "industry_type",
        "preferred_currency",
        "is_international",
        "created_at",
    )
    list_filter = ("preferred_currency", "is_international")
    search_fields = (
        "user__username",
        "user__email",
        "user__company_name",
        "tax_id",
        "industry_type",
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Standalone admin registration for direct Address management."""

    list_display = (
        "recipient_name",
        "user",
        "city",
        "state",
        "country",
        "is_default",
        "created_at",
    )
    list_filter = ("is_default", "country", "state")
    search_fields = (
        "recipient_name",
        "user__username",
        "user__email",
        "street_address",
        "city",
        "postal_code",
    )
