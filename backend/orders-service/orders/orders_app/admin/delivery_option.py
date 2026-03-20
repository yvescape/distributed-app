from django.contrib import admin
from ..models.delivery_option import DeliveryOption


@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "description",
        "amount",
        "currency",
        "position",
        "is_default",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_default",
        "currency",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = ("position",)

    list_editable = (
        "position",
        "is_active",
        "is_default",
    )

    readonly_fields = ("created_at",)