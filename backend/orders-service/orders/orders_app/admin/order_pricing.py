# admin/order_pricing.py
from django.contrib import admin
from ..models.order_pricing import OrderPricing


@admin.register(OrderPricing)
class OrderPricingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "subtotal",
        "delivery_price",
        "total",
        "currency",
    )

    list_filter = ("currency",)

    search_fields = ("order__id",)

    readonly_fields = ("id", "subtotal", "delivery_price", "total", "updated_at")