from django.urls import path
from ..views.register import RegisterView
from ..views.login import LoginView
from ..views.me import MeView
from ..views.update_user import UpdateUserView
from ..views.update_profile import UpdateProfileView
from ..views.user_list import UserListView
from ..views.toggle_user_status import ToggleUserStatusView
from ..views.audit_log_list import AuditLogListView


urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("users/me/", MeView.as_view()),
    path("users/update/", UpdateUserView.as_view()),
    path("users/profile/", UpdateProfileView.as_view()),
    path("users/", UserListView.as_view()),
    path("users/<uuid:user_id>/toggle/", ToggleUserStatusView.as_view()),
    path("audit-logs/", AuditLogListView.as_view()),
]