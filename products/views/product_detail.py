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
                "images", "specifications", "materials", "applications", "standards"))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        product = context.get("product")

        if product:
            from django.db.models import Count, Q, Case, When, Value, IntegerField, F
            
            material_ids = product.materials.values_list('id', flat=True)
            application_ids = product.applications.values_list('id', flat=True)
            standard_ids = product.standards.values_list('id', flat=True)

            related_qs = Product.objects.filter(is_active=True).exclude(id=product.id)

            related_qs = related_qs.annotate(
                same_category=Case(
                    When(category_id=product.category_id, then=Value(3)),
                    default=Value(0),
                    output_field=IntegerField()
                ),
                shared_materials=Count('materials', filter=Q(materials__in=material_ids), distinct=True),
                shared_apps=Count('applications', filter=Q(applications__in=application_ids), distinct=True),
                shared_stds=Count('standards', filter=Q(standards__in=standard_ids), distinct=True)
            ).annotate(
                score=F('same_category') + F('shared_materials') + F('shared_apps') + F('shared_stds')
            ).filter(score__gt=0).order_by('-score', '-created_at')[:4]
            
            # Fallback if we don't have enough related products
            if not related_qs.exists() and product.category:
                related_qs = Product.objects.filter(
                    category=product.category,
                    is_active=True
                ).exclude(id=product.id).order_by('-created_at')[:4]
                
            context["related_products"] = related_qs.select_related("category").prefetch_related("images", "materials")
        else:
            context["related_products"] = Product.objects.none()

        return context
