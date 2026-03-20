from django.contrib import admin
from ..models.user_audit_log import UserAuditLog


@admin.register(UserAuditLog)
class UserAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "ip_address",
        "timestamp",
    )

    list_filter = (
        "action",
        "timestamp",
    )

    search_fields = (
        "user__email",
        "ip_address",
    )

    readonly_fields = (
        "user",
        "action",
        "ip_address",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False