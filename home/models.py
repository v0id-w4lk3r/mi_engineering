from typing import TYPE_CHECKING
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

ALLOWED_ATTACHMENT_EXTENSIONS = [
    "xlsx",
    "xls",
    "csv",
    "pdf",
    "dwg",
    "dxf",
    "step",
    "stp",
    "iges",
    "igs",
    "png",
    "jpg",
    "jpeg",
    "webp",
    "zip",
]


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
    attachment = models.FileField(
        upload_to="contact_inquiries/%Y/%m/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_ATTACHMENT_EXTENSIONS)],
        verbose_name="Attachment",
        help_text="Upload RFQ spreadsheet (Excel/CSV) or technical drawings (PDF, CAD DWG/DXF/STEP, Images, ZIP up to 25 MB)",
    )
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
