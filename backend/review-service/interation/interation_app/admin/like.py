from django.contrib import admin
from ..models.like import Like


# 🔹 LIKE ADMIN
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user_id",
        "product_id",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user_id",
        "product_id",
    )

    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")
    list_per_page = 20