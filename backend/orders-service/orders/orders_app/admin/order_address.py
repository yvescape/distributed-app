# admin/order_address.py
from django.contrib import admin
from ..models.order_address import OrderAddress


@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "first_name",
        "last_name",
        "email",
        "mobile",
        "city",
    )

    search_fields = ("first_name", "last_name", "email", "order__id")

    readonly_fields = ("id",)