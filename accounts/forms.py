from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User


class ClientRegistrationForm(UserCreationForm):
    company_name = forms.CharField(
        max_length=255,
        required=False,
        label="Company Name"
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Phone Number"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "company_name", "phone_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enforce email requirement for client portal access
        self.fields["email"].required = True