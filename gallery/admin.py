from typing import Any
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Category,
    GalleryItem,
    GalleryImage,
    GalleryVideo,
    GalleryDocument,
    GalleryCertificate,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("display_order",)
    search_fields = ("name",)


class BaseGalleryAdmin(admin.ModelAdmin):
    """
    Base admin class for all media types. Hides the media_type field
    and forces the correct one upon save.
    """
    list_display = (
        "media_preview",
        "title",
        "category",
        "display_order",
        "is_active",
        "uploaded_at",
    )
    list_filter = ("is_active", "category", "uploaded_at")
    search_fields = ("title", "description", "category__name")
    list_editable = ("display_order", "is_active")

    # To be overridden by subclasses
    forced_media_type = None

    def save_model(self, request, obj, form, change):
        if self.forced_media_type:
            obj.media_type = self.forced_media_type
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.forced_media_type:
            return qs.filter(media_type=self.forced_media_type)
        return qs

    @admin.display(description="Preview")
    def media_preview(self, obj: GalleryItem) -> Any:
        if obj.media_type == GalleryItem.MediaType.IMAGE and obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        if obj.media_type == GalleryItem.MediaType.VIDEO:
            return mark_safe('<span style="font-size:20px;" title="Video">🎬</span>')
        if obj.media_type == GalleryItem.MediaType.CERTIFICATE:
            if obj.image:
                return format_html(
                    '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;" />',
                    obj.image.url,
                )
            if obj.document:
                return mark_safe('<span style="font-size:20px;" title="Certificate">📜</span>')
            return mark_safe(
                '<span style="color:#b45309;font-weight:600;" title="No file uploaded">⚠ No file</span>'
            )
        if obj.media_type == GalleryItem.MediaType.PDF:
            if obj.image:
                return format_html(
                    '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;" />',
                    obj.image.url,
                )
            if obj.document:
                return mark_safe('<span style="font-size:20px;" title="PDF">📄</span>')
            return mark_safe(
                '<span style="color:#b45309;font-weight:600;" title="No PDF uploaded">⚠ No file</span>'
            )
        return mark_safe('<span style="color:#9ca3af;">—</span>')


@admin.register(GalleryImage)
class GalleryImageAdmin(BaseGalleryAdmin):
    forced_media_type = GalleryItem.MediaType.IMAGE
    
    fieldsets = (
        ("Basic Info", {"fields": ("title", "category", "description")}),
        ("Image Upload", {"fields": ("image", "alt_text")}),
        ("SEO & Visibility", {"fields": ("meta_title", "meta_description", "display_order", "is_active")}),
    )


@admin.register(GalleryVideo)
class GalleryVideoAdmin(BaseGalleryAdmin):
    forced_media_type = GalleryItem.MediaType.VIDEO
    
    fieldsets = (
        ("Basic Info", {"fields": ("title", "category", "description")}),
        ("Video Upload", {
            "fields": ("video", "video_url"),
            "description": "Upload a video file or paste a YouTube/Vimeo URL."
        }),
        ("Thumbnail (Optional)", {
            "fields": ("image",),
            "description": "Upload an image to serve as a video thumbnail."
        }),
        ("SEO & Visibility", {"fields": ("meta_title", "meta_description", "alt_text", "display_order", "is_active")}),
    )


class GalleryDocumentForm(forms.ModelForm):
    media_type = forms.ChoiceField(
        choices=[
            (GalleryItem.MediaType.PDF, "Standard PDF Document"),
            (GalleryItem.MediaType.CERTIFICATE, "Certificate"),
        ],
        widget=forms.RadioSelect,
        initial=GalleryItem.MediaType.PDF,
        label="Document Type",
        help_text="Mark whether this file is a regular PDF Document or an official Certificate.",
    )

    class Meta:
        model = GalleryDocument
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial["media_type"] = self.instance.media_type or GalleryItem.MediaType.PDF


@admin.register(GalleryDocument)
class GalleryDocumentAdmin(BaseGalleryAdmin):
    form = GalleryDocumentForm
    forced_media_type = None
    
    list_display = (
        "media_preview",
        "title",
        "document_type_badge",
        "category",
        "display_order",
        "is_active",
        "uploaded_at",
    )
    list_filter = ("media_type", "is_active", "category", "uploaded_at")
    
    fieldsets = (
        ("Basic Info", {"fields": ("title", "category", "description")}),
        ("Document Classification", {
            "fields": ("media_type",),
            "description": "Mark whether this uploaded PDF is a standard PDF Document or an official Certificate."
        }),
        ("PDF Upload", {"fields": ("document",)}),
        ("Thumbnail / Cover Image (Optional)", {
            "fields": ("image",),
            "description": "Upload an image to serve as the document/certificate cover."
        }),
        ("SEO & Visibility", {"fields": ("meta_title", "meta_description", "alt_text", "display_order", "is_active")}),
    )

    def get_queryset(self, request):
        qs = super(BaseGalleryAdmin, self).get_queryset(request)
        return qs.filter(media_type__in=[GalleryItem.MediaType.PDF, GalleryItem.MediaType.CERTIFICATE])

    def save_model(self, request, obj, form, change):
        selected_type = form.cleaned_data.get("media_type")
        if selected_type in [GalleryItem.MediaType.PDF, GalleryItem.MediaType.CERTIFICATE]:
            obj.media_type = selected_type
        super().save_model(request, obj, form, change)

    @admin.display(description="Type")
    def document_type_badge(self, obj: GalleryItem) -> Any:
        if obj.media_type == GalleryItem.MediaType.CERTIFICATE:
            return mark_safe('<span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-weight:600;font-size:11px;">📜 Certificate</span>')
        return mark_safe('<span style="background:#f1f5f9;color:#475569;padding:2px 8px;border-radius:4px;font-weight:600;font-size:11px;">📄 PDF</span>')


@admin.register(GalleryCertificate)
class GalleryCertificateAdmin(BaseGalleryAdmin):
    forced_media_type = GalleryItem.MediaType.CERTIFICATE

    fieldsets = (
        ("Basic Info", {"fields": ("title", "category", "description")}),
        ("Certificate PDF Upload", {
            "fields": ("document",),
            "description": "Upload the certificate PDF file."
        }),
        ("Thumbnail / Cover Image (Optional)", {
            "fields": ("image",),
            "description": "Upload a scanned preview image of the certificate."
        }),
        ("SEO & Visibility", {"fields": ("meta_title", "meta_description", "alt_text", "display_order", "is_active")}),
    )
