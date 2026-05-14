# urls/interaction.py
from django.urls import path
from ..views.summary import ProductInteractionSummaryView
from ..views.comment import CommentListView, CommentCreateView, CommentUpdateView
from ..views.like import ToggleLikeView
from ..views.rating import RatingCreateUpdateView

urlpatterns = [
    # Public
    path("<uuid:product_id>/summary/", ProductInteractionSummaryView.as_view()),
    path("<uuid:product_id>/comments/", CommentListView.as_view()),

    # Auth required
    path("<uuid:product_id>/comments/create/", CommentCreateView.as_view()),
    path("<uuid:product_id>/comments/update/", CommentUpdateView.as_view()),  # ← ajouter
    path("<uuid:product_id>/toggle-like/", ToggleLikeView.as_view()),
    path("<uuid:product_id>/rating/", RatingCreateUpdateView.as_view()),
]