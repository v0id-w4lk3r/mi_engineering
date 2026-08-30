from typing import Any
from django.contrib import admin
from django.utils.html import format_html

# Import models from models.py instead of defining them here
from .models import Category, GalleryItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order")
    prepopulated_fields = {"slug": ("name", )}
    list_editable = ("display_order", )
    search_fields = ("name", )


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = (
        "media_preview",
        "title",
        "category",
        "media_type",
        "display_order",
        "is_active",
        "uploaded_at",
    )
    list_filter = ("media_type", "is_active", "category", "uploaded_at")
    search_fields = ("title", "description", "category__name")
    list_editable = ("display_order", "is_active")

    @admin.display(description="Preview")
    def media_preview(self, obj: GalleryItem) -> Any:
        if obj.media_type == GalleryItem.MediaType.IMAGE and obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url,
            )
        elif obj.media_type == GalleryItem.MediaType.VIDEO:
            return format_html(
                '<span style="color: #C62828; font-weight: bold;">[Video]</span>'
            )
        return "No Media"
