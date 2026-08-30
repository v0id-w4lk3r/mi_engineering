from typing import Any, Dict, Tuple
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

    list_display = ("username", "email", "first_name", "last_name", "role",
                    "company_name", "is_staff")

    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name",
                     "company_name")

    # Append custom fields to creation form fieldsets cleanly
    add_fieldsets = BaseUserAdmin.add_fieldsets + (("Custom Profile Info", {
        "fields": ("role", "company_name", "phone_number")
    }))

    def get_fieldsets(self, request: Any, obj: Any = None) -> Any:
        fieldsets = list(super().get_fieldsets(request, obj))
        custom_fieldset: Tuple[str, Dict[str, Any]] = ("Custom Profile Info", {
            "fields": ("role", "company_name", "phone_number")
        })
        return fieldsets + [custom_fieldset]
