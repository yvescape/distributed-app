# admin/order.py
from django.contrib import admin
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.order_address import OrderAddress
from ..models.order_pricing import OrderPricing


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("total",)


class OrderAddressInline(admin.StackedInline):
    model = OrderAddress
    extra = 0


class OrderPricingInline(admin.StackedInline):
    model = OrderPricing
    extra = 0
    readonly_fields = ("subtotal", "delivery_price", "total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user_id",
        "session_id",
        "status",
        "subtotal",
        "created_at",
    )

    list_filter = ("status", "created_at")

    search_fields = ("id",)

    readonly_fields = ("id", "created_at", "updated_at")

    inlines = [OrderItemInline, OrderAddressInline, OrderPricingInline]

    ordering = ("-created_at",)