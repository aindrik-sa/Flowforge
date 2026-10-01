from django.urls import path

from .views import AttachmentListCreateView, AttachmentDetailView

app_name = "attachments"

urlpatterns = [
    path(
        "tasks/<uuid:task_id>/attachments/",
        AttachmentListCreateView.as_view(),
        name="attachment-list-create",
    ),
    path(
        "attachments/<uuid:pk>/",
        AttachmentDetailView.as_view(),
        name="attachment-detail",
    ),
]
