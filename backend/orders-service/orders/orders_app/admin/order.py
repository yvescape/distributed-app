from django.contrib import admin
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.order_address import OrderAddress


# -----------------------------
# Order Items Inline
# -----------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("subtotal",)


# -----------------------------
# Address Inline
# -----------------------------
class OrderAddressInline(admin.StackedInline):
    model = OrderAddress
    extra = 0


# -----------------------------
# Order Admin
# -----------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer_name",
        "customer_email",
        "status",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "customer_name",
        "customer_email",
        "customer_phone",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    inlines = [
        OrderItemInline,
        OrderAddressInline,
    ]

    ordering = ("-created_at",)




