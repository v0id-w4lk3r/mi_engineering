from django.contrib import admin
from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "created_at", "is_processed")
    list_filter = ("is_processed", "created_at")
    search_fields = ("full_name", "email", "message")
    ordering = ("-created_at",)
    list_editable = ("is_processed",)
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Inquiry Information", {
            "fields": ("full_name", "email", "message", "created_at")
        }),
        ("Status Tracking", {
            "fields": ("is_processed",)
        })
    )