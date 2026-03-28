# orders_app/admin.py
from django.contrib import admin
from ..models.order_pricing import OrderPricing


@admin.register(OrderPricing)
class OrderPricingAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "subtotal", "delivery_price", "total", "currency", "updated_at")
    list_filter = ("currency",)
    search_fields = ("order__id", "order__customer_email")
    readonly_fields = ("id", "subtotal", "delivery_price", "total", "updated_at")

    fieldsets = (
        ("Commande", {
            "fields": ("id", "order")
        }),
        ("Livraison", {
            "fields": ("delivery_option",)
        }),
        ("Montants", {
            "fields": ("subtotal", "delivery_price", "total", "currency")
        }),
        ("Métadonnées", {
            "fields": ("updated_at",)
        }),
    )