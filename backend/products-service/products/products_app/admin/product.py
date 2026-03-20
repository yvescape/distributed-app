from django.contrib import admin
from django.utils.html import mark_safe
from ..models.product import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    # Colonnes affichées dans la liste
    list_display = (
        "id",
        "name",
        "image_preview",
        "category",
        "family",
        "gender",
        "price",
        "badge",
        "created_at",
    )

    list_filter = (
        "category",
        "family",
        "gender",
        "badge",
        "created_at",
    )

    search_fields = (
        "name",
        "notes_top",
        "notes_heart",
        "notes_base",
        "composition",
    )

    ordering = ("-created_at",)
    list_per_page = 20
    date_hierarchy = "created_at"

    readonly_fields = (
        "image_preview",
        "created_at",
        "updated_at",
    )

    fieldsets = (

        ("Informations principales", {
            "fields": (
                "name",
                "category",
                "price",
                "size",
                "image",
                "image_preview",
                "badge",
            )
        }),

        ("Classification", {
            "fields": (
                "family",
                "gender",
            )
        }),

        ("Notes olfactives", {
            "fields": (
                "notes_top",
                "notes_heart",
                "notes_base",
            )
        }),

        ("Composition & Conseils", {
            "fields": (
                "composition",
                "advice",
            )
        }),

        ("Dates", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    # 🔥 Image Preview
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image}" width="80" height="80" style="object-fit:cover;border-radius:8px;" />'
            )
        return "No Image"

    image_preview.short_description = "Aperçu"