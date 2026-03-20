from django.urls import path
from ..views.payment import PaymentCreateView, PaymentDetailView, PaymentListView


urlpatterns = [

    path(
        "",
        PaymentCreateView.as_view(),
        name="payment-create"
    ),

    path(
        "list/",
        PaymentListView.as_view(),
        name="payment-list"
    ),

    path(
        "<uuid:transaction_reference>/",
        PaymentDetailView.as_view(),
        name="payment-detail"
    ),
]