from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from ..models import Category, Product


class ProductListView(ListView):
    model = Product
    template_name = "product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related(
            "category").prefetch_related("images")

        # Category Filtering
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Search Query Filtering
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(short_description__icontains=search_query)
                | Q(material__icontains=search_query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get("category_slug")

        context["categories"] = Category.objects.filter(is_active=True)
        context["selected_category"] = category_slug
        context["category_obj"] = (get_object_or_404(
            Category, slug=category_slug) if category_slug else None)
        return context

    def render_to_response(self, context, **response_kwargs):
        is_htmx = self.request.headers.get("HX-Request") == "true"
        is_boosted = self.request.headers.get("HX-Boosted") == "true"
        target = self.request.headers.get("HX-Target")

        if is_htmx and not is_boosted and target == "catalog-content":
            return render(self.request, "partials/list/_product_grid.html",
                          context, **response_kwargs)

        # Default fallback: Render full page template (product_list.html)
        return super().render_to_response(context, **response_kwargs)
