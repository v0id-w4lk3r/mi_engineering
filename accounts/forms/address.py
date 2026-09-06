from typing import Any
from django import forms
from accounts.models import Address

INPUT_CLASS = (
    "w-full rounded-xl border border-gray-300 px-4 py-2 text-sm "
    "focus:border-[#C62828] focus:outline-none focus:ring-2 focus:ring-[#C62828]/20"
)

CHECKBOX_CLASS = "rounded border-gray-300 text-[#C62828] focus:ring-[#C62828]"


class AddressForm(forms.ModelForm):
    """Form to manage shipping/delivery addresses linked to a user profile."""

    class Meta:
        model = Address
        fields = [
            "recipient_name",
            "phone_number",
            "street_address",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
        ]
        widgets = {
            "recipient_name":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Full Name"
            }),
            "phone_number":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Phone Number"
            }),
            "street_address":
            forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": INPUT_CLASS,
                    "placeholder": "Street Address / Building / Suite"
                }),
            "city":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "City"
            }),
            "state":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "State / Province / Region"
            }),
            "postal_code":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "ZIP / Postal Code"
            }),
            "country":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Country"
            }),
            "is_default":
            forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
        }
