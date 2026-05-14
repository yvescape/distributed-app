# urls/order.py
from django.urls import path
from ..views.order import (
    UserOrderListView,
    OrderDetailView,
    OrderConfirmView,
    OrderCancelView,
    ClaimGuestOrdersView,
    CartCountView,
)

urlpatterns = [
    path("my/", UserOrderListView.as_view(), name="my-orders"),
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<uuid:pk>/confirm/", OrderConfirmView.as_view(), name="order-confirm"),
    path("<uuid:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("claim/", ClaimGuestOrdersView.as_view(), name="claim-guest-orders"),
    path("cart/count/", CartCountView.as_view(), name="cart-count"),
]