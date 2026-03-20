from django.contrib import admin
from ..models.order_pricing import OrderPricing


@admin.register(OrderPricing)
class OrderPricingAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "subtotal",
        "delivery_price",
        "total",
        "currency",
        "updated_at",
    )

    readonly_fields = (
        "subtotal",
        "delivery_price",
        "total",
        "updated_at",
    )

    search_fields = ("order__id",)