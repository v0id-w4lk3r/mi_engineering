from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ..models import ContactInquiry

MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB


class ContactInquiryAdminForm(forms.ModelForm):

    class Meta:
        model = ContactInquiry
        fields = "__all__"

    def clean_reply_attachment(self):
        attachment = self.cleaned_data.get("reply_attachment")
        if attachment and hasattr(attachment, "size"):
            if attachment.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    "Attachment size cannot exceed 25 MB.")
        return attachment


class CustomGroupAdminForm(forms.ModelForm):
    """App-wise segmented permission manager form for Django Admin."""

    class Meta:
        model = Group
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Fetch active ContentType IDs (filters out deleted models in installed apps)
        valid_content_types = [
            ct.id for ct in ContentType.objects.all()
            if ct.model_class() is not None
        ]

        # 2. Retrieve permissions belonging strictly to active models
        permissions = (Permission.objects.filter(
            content_type_id__in=valid_content_types).select_related(
                "content_type").order_by("content_type__app_label",
                                         "content_type__model", "codename"))

        self.app_permissions = {}
        for perm in permissions:
            app_label = perm.content_type.app_label
            if app_label not in self.app_permissions:
                self.app_permissions[app_label] = []
            self.app_permissions[app_label].append(perm)

        # 3. Create dynamically bound checkbox sets per app label
        for app_label, perms in self.app_permissions.items():
            field_name = f"perm_app_{app_label}"
            perm_ids = [p.id for p in perms]

            self.fields[field_name] = forms.ModelMultipleChoiceField(
                queryset=Permission.objects.filter(id__in=perm_ids),
                widget=forms.CheckboxSelectMultiple,
                required=False,
                label=app_label.capitalize(),
            )
            if self.instance.pk:
                self.fields[
                    field_name].initial = self.instance.permissions.filter(
                        id__in=perm_ids)

    def save(self, commit=True):
        group = super().save(commit=False)
        if commit:
            group.save()

        selected_permissions = []
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith("perm_app_") and value:
                selected_permissions.extend(value)

        group.permissions.set(selected_permissions)
        return group
