# urls/order_internal.py
from django.urls import path
from ..views.order_internal import InternalOrderConfirmView, InternalOrderCancelView

urlpatterns = [
    path("<uuid:pk>/confirm/", InternalOrderConfirmView.as_view(), name="internal-order-confirm"),
    path("<uuid:pk>/cancel/", InternalOrderCancelView.as_view(), name="internal-order-cancel"),
]