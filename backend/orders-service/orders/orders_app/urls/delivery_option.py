from django.urls import path
from ..views.delivery_option import (
    DeliveryOptionListView,
    DeliveryOptionDetailView,
    DeliveryOptionCreateView,
    DeliveryOptionUpdateView,
    DeliveryOptionDeleteView,
)

urlpatterns = [
    # Note: plus de "delivery-options/" ici
    path(
        "",
        DeliveryOptionListView.as_view(),
        name="delivery-options-list"
    ),
    path(
        "<uuid:pk>/",
        DeliveryOptionDetailView.as_view(),
        name="delivery-options-detail"
    ),
    path(
        "create/",
        DeliveryOptionCreateView.as_view(),
        name="delivery-options-create"
    ),
    path(
        "<uuid:pk>/update/",
        DeliveryOptionUpdateView.as_view(),
        name="delivery-options-update"
    ),
    path(
        "<uuid:pk>/delete/",
        DeliveryOptionDeleteView.as_view(),
        name="delivery-options-delete"
    ),
]