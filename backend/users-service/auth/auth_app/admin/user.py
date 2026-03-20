from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model


User = get_user_model()

class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "is_email_verified",
        "created_at",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_email_verified",
    )

    search_fields = ("email", "username")

    fieldsets = (
        ("Informations principales", {
            "fields": ("email", "username", "password")
        }),
        ("Informations personnelles", {
            "fields": ("first_name", "last_name")
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Statut Email", {
            "fields": ("is_email_verified",)
        }),
        ("Dates", {
            "fields": ("created_at", "last_login")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "username",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )

    readonly_fields = ("created_at", "last_login")


admin.site.register(User, UserAdmin)