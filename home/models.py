from typing import TYPE_CHECKING
from django.conf import settings
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

if TYPE_CHECKING:
    from accounts.models import ClientProfile  # type: ignore


class ContactInquiry(models.Model):
    if TYPE_CHECKING:
        id: int

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="contact_inquiries",
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_processed = models.BooleanField(default=False, db_index=True)

    # --- Staff Reply Section ---
    reply_message = CKEditor5Field(
        "Reply Message",
        config_name="default",
        blank=True,
        null=True,
    )
    reply_attachment = models.FileField(
        upload_to="email_reply_attachments/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Upload attachment (Max 25 MB)",
    )
    replied_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self) -> str:
        return f"Inquiry from {self.full_name} ({self.email})"

    @property
    def client_profile(self) -> "ClientProfile | None":
        """Returns the ClientProfile attached to the submitting user, if it exists."""
        if self.user and hasattr(self.user, "client_profile"):
            return getattr(self.user, "client_profile", None)
        return None
