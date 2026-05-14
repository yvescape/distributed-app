# admin/delivery_option.py
from django.contrib import admin
from ..models.delivery_option import DeliveryOption


@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "amount",
        "currency",
        "position",
        "is_active",
        "is_default",
    )

    list_filter = ("is_active", "is_default")

    search_fields = ("name",)

    readonly_fields = ("id", "created_at")

    ordering = ("position",)