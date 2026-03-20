from django.urls import path
from ..views.summary import ProductInteractionSummaryView
from ..views.comment import CommentListView
from ..views.comment import CommentCreateView
from ..views.like import  ToggleLikeView
from ..views.rating import RatingCreateUpdateView

urlpatterns = [
    # Public
    path("interactions/<uuid:product_id>/summary/", ProductInteractionSummaryView.as_view()),
    path("interactions/<uuid:product_id>/comments/", CommentListView.as_view()),

    # Auth required
    path("interactions/comments/create/", CommentCreateView.as_view()),
    path("interactions/<uuid:product_id>/toggle-like/", ToggleLikeView.as_view()),
    path("interactions/rating/", RatingCreateUpdateView.as_view()),
]