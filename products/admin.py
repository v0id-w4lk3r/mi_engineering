from django.contrib import admin
from .models import Category, Product, ProductImage, ProductSpecification


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 2


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active", )
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name", )}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "material",
        "grade",
        "is_featured",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active", "is_featured", "material")
    search_fields = ("title", "description", "material", "grade", "standard")
    prepopulated_fields = {"slug": ("title", )}
    inlines = [ProductImageInline, ProductSpecificationInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image", "alt_text", "is_primary")
    list_filter = ("is_primary", "product")
    search_fields = ("product__title", "alt_text")


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ("product", "key", "value")
    list_filter = ("key", "product")
    search_fields = ("key", "value", "product__title")
