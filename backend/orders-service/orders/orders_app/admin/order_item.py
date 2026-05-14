# admin/order_item.py
from django.contrib import admin
from ..models.order_item import OrderItem


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product_name",
        "price",
        "quantity",
        "total",
    )

    search_fields = ("product_name", "order__id")

    readonly_fields = ("id", "total")