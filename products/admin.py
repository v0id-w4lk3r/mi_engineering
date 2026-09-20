from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage, ProductSpecification, Application, Standard, Material

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "image")}),
        (
            "SEO & Meta Tags",
            {
                "classes": ("collapse",),
                "fields": ("meta_title", "meta_description", "meta_keywords"),
            },
        ),
    )

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "image")}),
        (
            "SEO & Meta Tags",
            {
                "classes": ("collapse",),
                "fields": ("meta_title", "meta_description", "meta_keywords"),
            },
        ),
    )

@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "description")}),
        (
            "SEO & Meta Tags",
            {
                "classes": ("collapse",),
                "fields": ("meta_title", "meta_description", "meta_keywords"),
            },
        ),
    )

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
    fieldsets = (
        (
            None,
            {"fields": ("name", "slug", "description", "image", "is_active")},
        ),
        (
            "SEO & Meta Tags",
            {
                "classes": ("collapse",),
                "fields": ("meta_title", "meta_description", "meta_keywords"),
            },
        ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "primary_thumbnail",
        "title",
        "category",
        "display_material",
        "is_featured",
        "is_active",
    )
    list_editable = ("is_featured", "is_active")
    list_filter = ("category", "is_active", "is_featured", "materials", "material")
    search_fields = ("title", "materials__name", "material", "grade")
    prepopulated_fields = {"slug": ("title", )}
    filter_horizontal = ("materials", "applications", "standards")
    inlines = [ProductImageInline, ProductSpecificationInline]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "materials",
                    "applications",
                    "standards",
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "Specifications & Attributes",
            {
                "fields": ("material", "grade", "size_range")
            },
        ),
        (
            "Technical Specifications",
            {
                "classes": ("collapse", ),
                "fields": ("chemical_composition", "mechanical_properties"),
            },
        ),
        (
            "SEO & Meta Tags",
            {
                "classes": ("collapse", ),
                "fields": ("meta_title", "meta_description", "meta_keywords"),
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

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if form.instance.materials.exists():
            mat_names = ", ".join(m.name for m in form.instance.materials.all())
            if not form.instance.material or form.instance.material != mat_names:
                form.instance.material = mat_names
                form.instance.save(update_fields=["material"])
        elif form.instance.material:
            mat = Material.objects.filter(name__iexact=form.instance.material.strip()).first()
            if mat:
                form.instance.materials.add(mat)
