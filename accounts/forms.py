from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import ClientProfile, User

# Common styling class for form input fields (Module level)
INPUT_CLASS = (
    "w-full rounded-xl border border-gray-300 px-4 py-2 "
    "focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
)


class ClientRegistrationForm(UserCreationForm):
    """Form handling new client account registration."""

    company_name = forms.CharField(
        max_length=255,
        required=False,
        label="Company Name",
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Phone Number",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "company_name", "phone_number")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Enforce email requirement for client portal access
        self.fields["email"].required = True


class ClientProfileForm(forms.ModelForm):
    """Form for updating client business details, contact information, and shipping addresses."""

    company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )

    class Meta:
        model = ClientProfile
        fields = [
            "tax_id",
            "industry_type",
            "billing_address",
            "shipping_address",
            "city",
            "state",
            "postal_code",
            "country"
        ]
        widgets = {
            "tax_id":
            forms.TextInput(attrs={"class": INPUT_CLASS}),
            "industry_type":
            forms.TextInput(attrs={"class": INPUT_CLASS}),
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
            forms.TextInput(attrs={"class": INPUT_CLASS}),
            "postal_code":
            forms.TextInput(attrs={"class": INPUT_CLASS}),
            "country":
            forms.TextInput(attrs={"class": INPUT_CLASS}),
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
