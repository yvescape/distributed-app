from django.contrib import admin
from ..models.prepay_cart import SavedPrepaidCard


@admin.register(SavedPrepaidCard)
class SavedPrepaidCardAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user_id",
        "card_holder",
        "masked_card_number",
        "expiration_date",
        "created_at",
    )

    search_fields = (
        "user_id",
        "card_holder",
        "card_number",
    )

    list_filter = (
        "created_at",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = ("-created_at",)

    list_per_page = 25

    def masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"
    
    masked_card_number.short_description = "Card Number"