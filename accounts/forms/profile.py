from typing import Any
from django import forms
from accounts.models import ClientProfile, User

INPUT_CLASS = (
    "w-full rounded-xl border border-gray-300 px-4 py-2 text-sm "
    "focus:border-[#C62828] focus:outline-none focus:ring-2 focus:ring-[#C62828]/20"
)

CHECKBOX_CLASS = "rounded border-gray-300 text-[#C62828] focus:ring-[#C62828]"


class ClientProfileForm(forms.ModelForm):
    """Form for updating client profile operational attributes."""

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
            "tax_id",
            "industry_type",
            "preferred_currency",
            "is_international",
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
            "preferred_currency":
            forms.Select(attrs={"class": INPUT_CLASS}),
            "is_international":
            forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
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
