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


from django import forms
from django.forms import widgets

class DatalistWidget(widgets.TextInput):
    def __init__(self, datalist, *args, **kwargs):
        self.datalist = datalist
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        list_id = f"datalist_{name}"
        if attrs is None:
            attrs = {}
        attrs['list'] = list_id
        html = super().render(name, value, attrs, renderer)
        datalist_html = f'<datalist id="{list_id}">' + "".join(f'<option value="{item}">' for item in self.datalist) + '</datalist>'
        return html + datalist_html

class ProductSpecificationForm(forms.ModelForm):
    class Meta:
        model = ProductSpecification
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.db.utils import OperationalError, ProgrammingError
        try:
            db_keys = set(ProductSpecification.objects.values_list('key', flat=True).distinct())
        except (OperationalError, ProgrammingError):
            db_keys = set()
            
        defaults = {
            'Length Size', 'Class', 'Thread Type', 'Surface Finish', 
            'Strength Features', 'Manufacturing Process', 'Customization', 'Mark'
        }
        all_keys = sorted(list(db_keys | defaults))
        self.fields['key'].widget = DatalistWidget(datalist=all_keys)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    form = ProductSpecificationForm
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
    list_filter = ("category", "is_active", "is_featured", "materials")
    search_fields = ("title", "materials__name", "grade")
    prepopulated_fields = {"slug": ("title", )}
    autocomplete_fields = ("materials", "applications", "standards")
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
                "fields": ("specification_system", "grade", "size_range")
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

    def get_queryset(self, request):
        """Optimize list view performance by prefetching related models."""
        qs = super().get_queryset(request)
        return qs.prefetch_related("materials", "images")

    def primary_thumbnail(self, obj):
        img = obj.primary_image
        if img and img.image:
            return format_html(
                '<img src="{}" style="max-height: 32px; max-width: 32px; object-fit: cover; border-radius: 4px;" />',
                img.image.url,
            )
        return "—"

    primary_thumbnail.short_description = "Image"
