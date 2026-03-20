from django.contrib import admin
from ..models.user_profile import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone_number",
        "country",
    )

    search_fields = (
        "user__email",
        "phone_number",
    )

    list_filter = ("country",)