from django import forms
from utils.validators import validate_not_disposable_email
from ..models import ALLOWED_ATTACHMENT_EXTENSIONS, ContactInquiry

MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25 MB


class ContactForm(forms.ModelForm):

    class Meta:
        model = ContactInquiry
        fields = ["full_name", "email", "message", "attachment"]
        widgets = {
            "full_name":
            forms.TextInput(
                attrs={
                    "class":
                    ("w-full px-4 py-3 rounded-xl border border-brand-border"
                     " focus:ring-2 focus:ring-brand-accent focus:outline-none"
                     ),
                    "placeholder":
                    "John Doe",
                }),
            "email":
            forms.EmailInput(
                attrs={
                    "class":
                    ("w-full px-4 py-3 rounded-xl border border-brand-border"
                     " focus:ring-2 focus:ring-brand-accent focus:outline-none"
                     ),
                    "placeholder":
                    "john@company.com",
                }),
            "message":
            forms.Textarea(
                attrs={
                    "rows":
                    4,
                    "class":
                    ("w-full px-4 py-3 rounded-xl border border-brand-border"
                     " focus:ring-2 focus:ring-brand-accent focus:outline-none"
                     ),
                    "placeholder": (
                        "Specify dimensions, material grade, and quantity..."),
                }),
            "attachment":
            forms.FileInput(
                attrs={
                    "id":
                    "id_attachment",
                    "accept": (
                        ".xlsx,.xls,.csv,.pdf,.dwg,.dxf,.step,.stp,.iges,.igs,"
                        ".png,.jpg,.jpeg,.webp,.zip"
                    ),
                }),
        }

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email")
        if email:
            validate_not_disposable_email(email)
        return email or ""

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if attachment and hasattr(attachment, "size"):
            if attachment.size > MAX_ATTACHMENT_SIZE:
                raise forms.ValidationError(
                    "Attachment size cannot exceed 25 MB.")
        return attachment

