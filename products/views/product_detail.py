from typing import Any
from django.views.generic import DetailView
from ..models import Product


class ProductDetailView(DetailView):
    model = Product
    template_name = "product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (Product.objects.filter(
            is_active=True).select_related("category").prefetch_related(
                "images", "specifications"))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        product = context.get("product")

        if product and product.category:
            context["related_products"] = (Product.objects.filter(
                category=product.category,
                is_active=True).exclude(id=product.id).select_related(
                    "category").prefetch_related("images")[:4])
        else:
            context["related_products"] = Product.objects.none()

        return context
