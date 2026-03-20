from django.contrib import admin
from ..models.order_address import OrderAddress


# -----------------------------
# Address Admin
# -----------------------------
@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "city",
        "postal_code",
    )

    search_fields = (
        "city",
        "postal_code",
        "order__id",
    )

    readonly_fields = ("id",)