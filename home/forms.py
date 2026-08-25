from django import forms
from utils.validators import validate_not_disposable_email
from .models import ContactInquiry


class ContactForm(forms.ModelForm):

    class Meta:
        model = ContactInquiry
        fields = ["full_name", "email", "message"]
        widgets = {
            "full_name":
            forms.TextInput(
                attrs={
                    "class":
                    "w-full px-4 py-3 rounded-xl border border-brand-border focus:ring-2 focus:ring-brand-accent focus:outline-none",
                    "placeholder": "John Doe",
                }),
            "email":
            forms.EmailInput(
                attrs={
                    "class":
                    "w-full px-4 py-3 rounded-xl border border-brand-border focus:ring-2 focus:ring-brand-accent focus:outline-none",
                    "placeholder": "john@company.com",
                }),
            "message":
            forms.Textarea(
                attrs={
                    "rows":
                    4,
                    "class":
                    "w-full px-4 py-3 rounded-xl border border-brand-border focus:ring-2 focus:ring-brand-accent focus:outline-none",
                    "placeholder":
                    "Specify dimensions, material grade, and quantity...",
                }),
        }

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email")
        if email:
            validate_not_disposable_email(email)
        return email or ""
