from django.contrib import admin
from ..models.payment import Payment
from django.utils.html import format_html


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order_pricing_id",
        "amount",
        "currency",
        "colored_status",  # ← Ajout de la méthode ici
        "transaction_reference",
        "created_at",
    )

    list_filter = (
        "status",
        "currency",
        "created_at",
    )

    search_fields = (
        "order_pricing_id",
        "transaction_reference",
    )

    readonly_fields = (
        "id",
        "transaction_reference",
        "created_at",
    )

    ordering = ("-created_at",)

    list_per_page = 25
    
    def colored_status(self, obj):
        if obj.status == "success":
            color = "green"
        else:
            color = "red"

        return format_html(
            '<strong style="color:{};">{}</strong>',
            color,
            obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status
        )

    colored_status.short_description = "Status"
    colored_status.admin_order_field = "status"  # ← Permet de trier par cette colonne