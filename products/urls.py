from django.urls import path
from products.views import (
    ProductDetailView,
    ProductListView,
    ApplicationListView,
    StandardListView,
)

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("category/<slug:category_slug>/",
         ProductListView.as_view(),
         name="category_product_list"),
    
    path("applications/", ApplicationListView.as_view(), name="application_list"),
    path("applications/<slug:application_slug>/",
         ProductListView.as_view(),
         name="application_product_list"),

    path("standards/", StandardListView.as_view(), name="standard_list"),
    path("standards/<slug:standard_slug>/",
         ProductListView.as_view(),
         name="standard_product_list"),

    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
