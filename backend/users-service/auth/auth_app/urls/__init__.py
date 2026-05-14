from django.urls import path
from ..views.register import RegisterView
from ..views.login import LoginView
from ..views.me import MeView
from ..views.update_user import UpdateUserView
from ..views.user_list import UserListView
from ..views.toggle_user_status import ToggleUserStatusView
from ..views.audit_log_list import AuditLogListView


urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("", LoginView.as_view()),
    path("me/", MeView.as_view()),
    path("update/", UpdateUserView.as_view()),
    path("list/", UserListView.as_view()),
    path("<uuid:user_id>/toggle/", ToggleUserStatusView.as_view()),
    path("audit-logs/", AuditLogListView.as_view()),
]