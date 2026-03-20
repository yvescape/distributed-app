from django.contrib import admin
from ..models.order_item import OrderItem


# -----------------------------
# Order Item Admin
# -----------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product_name",
        "price",
        "quantity",
        "subtotal",
    )

    search_fields = (
        "product_name",
        "order__id",
    )

    readonly_fields = ("id",)