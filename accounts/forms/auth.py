from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User

INPUT_CLASS = (
    "w-full rounded-xl border border-gray-300 px-4 py-2 text-sm "
    "focus:border-[#C62828] focus:outline-none focus:ring-2 focus:ring-[#C62828]/20"
)


class ClientRegistrationForm(UserCreationForm):
    """Form handling new client account registration."""

    company_name = forms.CharField(
        max_length=255,
        required=False,
        label="Company Name",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )
    phone_number = forms.CharField(
        max_length=30,
        required=False,
        label="Phone Number (with country code)",
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASS,
            "placeholder": "+1 555 019 2831"
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "company_name", "phone_number")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        for field_name in self.fields:
            if field_name not in ["company_name", "phone_number"]:
                self.fields[field_name].widget.attrs.update(
                    {"class": INPUT_CLASS})
