from typing import Any, Dict
from django.db.models import QuerySet
from django.views.generic import DetailView, ListView

from .models import Category, GalleryItem


class GalleryListView(ListView):
    """
    Public class-based view listing active gallery items (Images & Videos).
    Supports category and media type filtering.
    """

    model = GalleryItem
    template_name = "gallery_list.html"
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self) -> QuerySet[GalleryItem]:
        queryset = (GalleryItem.objects.filter(
            is_active=True).select_related("category").order_by(
                "display_order", "-uploaded_at"))

        # Filter by Category Slug
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by Media Type (IMAGE / VIDEO)
        media_type = self.request.GET.get("type")
        if media_type in [
                GalleryItem.MediaType.IMAGE, GalleryItem.MediaType.VIDEO
        ]:
            queryset = queryset.filter(media_type=media_type)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by(
            "display_order", "name")
        context["active_category"] = self.request.GET.get("category", "")
        context["active_type"] = self.request.GET.get("type", "")
        return context


class GalleryDetailView(DetailView):
    """Class-based view for rendering a single gallery item's details."""

    model = GalleryItem
    template_name = "gallery_detail.html"
    context_object_name = "item"

    def get_queryset(self) -> QuerySet[GalleryItem]:
        return GalleryItem.objects.filter(
            is_active=True).select_related("category")
