from django.urls import path
from ..views.product import ProductListView, ProductDetailView

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<uuid:id>/", ProductDetailView.as_view(), name="product-detail"),
]