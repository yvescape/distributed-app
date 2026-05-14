# urls/delivery_option.py
from django.urls import path
from ..views.delivery_option import DeliveryOptionListView, DeliveryOptionDetailView

urlpatterns = [
    path("", DeliveryOptionListView.as_view(), name="delivery-option-list"),
    path("<uuid:pk>/", DeliveryOptionDetailView.as_view(), name="delivery-option-detail"),
]