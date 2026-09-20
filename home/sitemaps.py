from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Application, Category, Material, Product, Standard


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages (home, about, contact, etc.)."""
    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return [
            "home:homepage",
            "home:about-us",
            "home:contact-us",
            "products:product_list",
            "products:application_list",
            "products:standard_list",
            "products:material_list",
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    """Sitemap for individual product detail pages."""
    changefreq = "weekly"
    priority = 0.9
    protocol = "https"

    def items(self):
        return Product.objects.filter(is_active=True).select_related("category")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("products:product_detail", kwargs={"slug": obj.slug})


class CategorySitemap(Sitemap):
    """Sitemap for product category listing pages."""
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return reverse(
            "products:category_product_list",
            kwargs={"category_slug": obj.slug},
        )


class ApplicationSitemap(Sitemap):
    """Sitemap for products filtered by application."""
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Application.objects.all().order_by("name")

    def location(self, obj):
        return reverse(
            "products:application_product_list",
            kwargs={"application_slug": obj.slug},
        )


class StandardSitemap(Sitemap):
    """Sitemap for products filtered by standard."""
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Standard.objects.all().order_by("name")

    def location(self, obj):
        return reverse(
            "products:standard_product_list",
            kwargs={"standard_slug": obj.slug},
        )


class MaterialSitemap(Sitemap):
    """Sitemap for products filtered by material."""
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Material.objects.all().order_by("name")

    def location(self, obj):
        return reverse(
            "products:material_product_list",
            kwargs={"material_slug": obj.slug},
        )
