# urls/order_address.py
from django.urls import path
from ..views.order_address import OrderAddressCreateUpdateView, OrderAddressDetailView

urlpatterns = [
    path("", OrderAddressCreateUpdateView.as_view(), name="cart-address"),
    path("<uuid:pk>/", OrderAddressDetailView.as_view(), name="cart-address-detail"),
]