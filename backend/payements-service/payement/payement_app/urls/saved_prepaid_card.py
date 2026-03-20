from django.urls import path
from ..views.saved_prepaid_card import SavedPrepaidCardListCreateView,SavedPrepaidCardDeleteView


urlpatterns = [

    path(
        "",
        SavedPrepaidCardListCreateView.as_view(),
        name="saved-cards"
    ),

    path(
        "<uuid:pk>/",
        SavedPrepaidCardDeleteView.as_view(),
        name="saved-card-delete"
    ),
]