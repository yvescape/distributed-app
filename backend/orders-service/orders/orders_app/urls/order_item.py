# urls/order_item.py
from django.urls import path
from ..views.order_item import (
    OrderItemListCreateView,
    OrderItemDetailView,
    OrderItemQuantityView,
    ProductInCartView
)

urlpatterns = [
    path("cart/items/", OrderItemListCreateView.as_view(), name="cart-items"),
    path("cart/items/<uuid:pk>/", OrderItemDetailView.as_view(), name="cart-item-detail"),
    path("cart/items/<uuid:pk>/quantity/", OrderItemQuantityView.as_view(), name="cart-item-quantity"),
    path("check/<str:product_id>/", ProductInCartView.as_view()),
]