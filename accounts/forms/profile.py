from typing import Any
from django import forms
from accounts.models import User

INPUT_CLASS = (
    "w-full rounded-xl border border-gray-300 px-4 py-2 text-sm "
    "focus:border-[#C62828] focus:outline-none focus:ring-2 focus:ring-[#C62828]/20"
)


class UserProfileForm(forms.ModelForm):
    """Form for updating basic user account information."""

    class Meta:
        model = User
        fields = ["company_name", "phone_number"]
        widgets = {
            "company_name":
            forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "e.g. Acme Engineering Corp",
                }),
            "phone_number":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "+91 98765 43210",
            }),
        }
