from django.urls import path
from ..views.order_pricing import (
    OrderPricingListView,
    OrderPricingDetailView,
    UpdateDeliveryOptionView,
)

urlpatterns = [
    path("", OrderPricingListView.as_view(), name="order-pricing-list"),
    path("<uuid:pk>/", OrderPricingDetailView.as_view(), name="order-pricing-detail"),
    path("delivery/", UpdateDeliveryOptionView.as_view(), name="update-delivery-option"),
]