from django.urls import path
from products.views import ProductDetailView, ProductListView

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("category/<slug:category_slug>/",
         ProductListView.as_view(),
         name="category_product_list"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
