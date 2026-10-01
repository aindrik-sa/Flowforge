from django.urls import path

from .views import CommentListCreateView, CommentDetailView

app_name = "comments"

urlpatterns = [
    path(
        "tasks/<uuid:task_id>/comments/",
        CommentListCreateView.as_view(),
        name="comment-list-create",
    ),
    path(
        "comments/<uuid:pk>/",
        CommentDetailView.as_view(),
        name="comment-detail",
    ),
]
