from typing import Any, Dict, Tuple
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


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

    # Filters available in the right sidebar
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    # Search fields
    search_fields = ("username", "email", "first_name", "last_name",
                     "company_name")

    def get_fieldsets(self, request: Any, obj: Any = None) -> Any:
        fieldsets = list(super().get_fieldsets(request, obj))
        custom_fieldset: Tuple[str, Dict[str, Any]] = (
            "Custom Profile Info",
            {
                "fields": ("role", "company_name", "phone_number")
            },
        )
        return fieldsets + [custom_fieldset]

    def get_form(self, request: Any, obj: Any = None, **kwargs: Any) -> Any:
        # Dynamically append custom fields when adding a new user
        if obj is None and self.add_fieldsets:
            custom_fieldset: Tuple[str, Dict[str, Any]] = (
                "Custom Profile Info",
                {
                    "fields": ("role", "company_name", "phone_number")
                }
            )
            self.add_fieldsets = tuple(
                self.add_fieldsets) + (custom_fieldset, )
        return super().get_form(request, obj, **kwargs)
