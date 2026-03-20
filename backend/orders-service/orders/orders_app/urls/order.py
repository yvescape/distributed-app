from django.urls import path
from ..views.order import OrderCreateView, UserOrderListView, OrderDetailView, OrderStatusUpdateView

urlpatterns = [
    # Note: plus de "orders/" ici car on l'a mis dans __init__.py
    path(
        "",
        OrderCreateView.as_view(),
        name="create-order"
    ),
    path(
        "my/",
        UserOrderListView.as_view(),
        name="my-orders"
    ),
    path(
        "<uuid:pk>/",
        OrderDetailView.as_view(),
        name="order-detail"
    ),
    path(
        "<uuid:pk>/status/",
        OrderStatusUpdateView.as_view(),
        name="order-status-update"
    )
]