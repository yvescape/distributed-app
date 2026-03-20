from django.contrib import admin
from ..models.comment import Comment


# 🔹 COMMENT ADMIN
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "short_content",
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
        "content",
    )

    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    list_per_page = 20

    # 🔥 Affichage court du commentaire
    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    short_content.short_description = "Comment"