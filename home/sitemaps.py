from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Category, Product


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
