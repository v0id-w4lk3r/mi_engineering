from typing import Any
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.html import strip_tags

from .forms import ContactInquiryAdminForm, CustomGroupAdminForm
from .models import ContactInquiry

# Unregister standard Group admin to replace with custom app-wise permission panel
admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(admin.ModelAdmin):
    form = CustomGroupAdminForm
    change_form_template = "admin/custom_group_change_form.html"

    def change_view(
        self,
        request: Any,
        object_id: str,
        form_url: str = "",
        extra_context: Any = None,
    ) -> Any:
        extra_context = extra_context or {}
        group = self.get_object(request, object_id)
        if group:
            form = self.get_form(request, group)(instance=group)
            extra_context["app_permissions"] = getattr(form, "app_permissions",
                                                       {})
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    form = ContactInquiryAdminForm

    list_display = (
        "full_name",
        "email",
        "user_link",
        "created_at",
        "is_processed",
        "replied_at",
    )
    list_filter = ("is_processed", "created_at")
    search_fields = ("full_name", "email", "message", "user__username")
    ordering = ("-created_at", )
    list_editable = ("is_processed", )
    readonly_fields = ("created_at", "replied_at", "client_info_summary")

    fieldsets = (
        (
            "Client Details",
            {
                "fields": ("user", "client_info_summary", "full_name", "email")
            },
        ),
        ("Inquiry Content", {
            "fields": ("message", "created_at")
        }),
        (
            "Staff Reply Section",
            {
                "fields": (
                    "is_processed",
                    "reply_message",
                    "reply_attachment",
                    "replied_at",
                )
            },
        ),
    )

    @admin.display(description="Client Account")
    def user_link(self, obj: ContactInquiry) -> str:
        return str(obj.user) if obj.user else "Anonymous"

    @admin.display(description="Client Info Summary")
    def client_info_summary(self, obj: ContactInquiry) -> str:
        if not obj.user:
            return "Anonymous User / No registered account"

        company = getattr(obj.user, "company_name", None) or "N/A"
        phone = getattr(obj.user, "phone_number", None) or "N/A"
        role = obj.user.get_role_display() if hasattr(obj.user, "get_role_display") else str(getattr(obj.user, "role", "Client"))

        return f"Company: {company} | Phone: {phone} | Role: {role} | Registered Email: {obj.user.email}"

    def save_model(self, request: Any, obj: ContactInquiry, form: Any,
                   change: bool) -> None:
        super().save_model(request, obj, form, change)

        if "reply_message" in form.changed_data and obj.reply_message:
            html_content = obj.reply_message
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject="Re: Inquiry - M.I. Engineering Works",
                body=text_content,
                to=[obj.email],
            )
            email.attach_alternative(html_content, "text/html")

            if obj.reply_attachment:
                try:
                    email.attach_file(obj.reply_attachment.path)
                except Exception as attach_err:
                    self.message_user(
                        request,
                        f"Could not attach file: {attach_err}",
                        level=messages.WARNING,
                    )

            try:
                email.send(fail_silently=False)
                obj.is_processed = True
                obj.replied_at = timezone.now()
                obj.save(update_fields=["is_processed", "replied_at"])
                self.message_user(
                    request,
                    f"Reply successfully sent to {obj.email}",
                    level=messages.SUCCESS,
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to send email: {e}",
                    level=messages.ERROR,
                )
