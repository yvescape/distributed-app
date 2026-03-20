from django.urls import path
from ..views.order_pricing import OrderPricingDetailView

urlpatterns = [
    # Order Pricing

    path(
        "orders/<uuid:order_id>/pricing/",
        OrderPricingDetailView.as_view(),
        name="order-pricing-detail"
    ),
]

