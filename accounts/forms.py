from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import ClientProfile, User

# Common styling class for form input fields
INPUT_CLASS = (
    "w-full rounded-xl border border-gray-300 px-4 py-2 text-sm "
    "focus:border-[#C62828] focus:outline-none focus:ring-2 focus:ring-[#C62828]/20"
)

CHECKBOX_CLASS = (
    "rounded border-gray-300 text-[#C62828] focus:ring-[#C62828]")


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


class ClientProfileForm(forms.ModelForm):
    """Form for updating domestic and international client profile details."""

    company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )
    phone_number = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASS,
            "placeholder": "+44 20 7946 0912"
        }),
    )

    class Meta:
        model = ClientProfile
        fields = [
            "company_name",
            "phone_number",
            "tax_id",
            "industry_type",
            "country",
            "preferred_currency",
            "is_international",
            "billing_address",
            "shipping_address",
            "city",
            "state",
            "postal_code",
        ]
        widgets = {
            "tax_id":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "GSTIN / VAT / EIN / TIN"
            }),
            "industry_type":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "e.g. Aerospace, Automotive"
            }),
            "country":
            forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "e.g. United States, Germany, India"
                }),
            "preferred_currency":
            forms.Select(attrs={"class": INPUT_CLASS}),
            "is_international":
            forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "billing_address":
            forms.Textarea(attrs={
                "rows": 3,
                "class": INPUT_CLASS
            }),
            "shipping_address":
            forms.Textarea(attrs={
                "rows": 3,
                "class": INPUT_CLASS
            }),
            "city":
            forms.TextInput(attrs={"class": INPUT_CLASS}),
            "state":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "State / Province / Region"
            }),
            "postal_code":
            forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "ZIP / Postcode"
            }),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance,
                                     "user") and self.instance.user:
            self.fields[
                "company_name"].initial = self.instance.user.company_name
            self.fields[
                "phone_number"].initial = self.instance.user.phone_number

    def save(self, commit: bool = True) -> ClientProfile:
        profile: ClientProfile = super().save(commit=False)
        user: User = profile.user

        user.company_name = self.cleaned_data.get("company_name")
        user.phone_number = self.cleaned_data.get("phone_number")

        if commit:
            user.save()
            profile.save()

        return profile
