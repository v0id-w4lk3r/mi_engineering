from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage, ProductSpecification


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("image_preview", )
    fields = ("image", "image_preview", "alt_text", "is_primary")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 40px; border-radius: 4px;" />',
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Preview"


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active", )
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name", )}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "primary_thumbnail",
        "title",
        "category",
        "min_order_quantity",
        "material",
        "is_featured",
        "is_active",
    )
    list_editable = ("min_order_quantity", "is_featured", "is_active")
    list_filter = ("category", "is_active", "is_featured", "material")
    search_fields = ("title", "material", "grade", "standard")
    prepopulated_fields = {"slug": ("title", )}
    raw_id_fields = ("category", )
    inlines = [ProductImageInline, ProductSpecificationInline]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "short_description",
                    "description",
                )
            },
        ),
        ("Minimum Order Quantity", {
            "fields": ("min_order_quantity", )
        }),
        (
            "Specifications & Attributes",
            {
                "fields": ("material", "grade", "standard", "size_range")
            },
        ),
        (
            "Technical Specifications",
            {
                "classes": ("collapse", ),
                "fields": ("chemical_composition", "mechanical_properties"),
            },
        ),
        ("Visibility", {
            "fields": ("is_featured", "is_active")
        }),
    )

    def primary_thumbnail(self, obj):
        img = obj.primary_image
        if img and img.image:
            return format_html(
                '<img src="{}" style="max-height: 32px; max-width: 32px; object-fit: cover; border-radius: 4px;" />',
                img.image.url,
            )
        return "—"

    primary_thumbnail.short_description = "Image"
