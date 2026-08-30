from django.urls import path
from .views import GalleryDetailView, GalleryListView

app_name = "gallery"

urlpatterns = [
    path("", GalleryListView.as_view(), name="gallery_list"),
    path("<int:pk>/", GalleryDetailView.as_view(), name="gallery_detail"),
]
