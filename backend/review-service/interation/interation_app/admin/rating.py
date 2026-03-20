from django.contrib import admin
from ..models.rating import Rating


# 🔹 RATING ADMIN
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user_id",
        "product_id",
        "value",
        "created_at",
    )

    list_filter = (
        "value",
        "created_at",
    )

    search_fields = (
        "user_id",
        "product_id",
    )

    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")
    list_per_page = 20