from django.urls import path

from .views import (
    WorkspaceDetailView,
    ProjectListCreateView,
    ProjectDetailView,
    ProjectMemberListView,
    ProjectMemberDetailView,
    BoardListCreateView,
    BoardDetailView,
    BoardColumnListCreateView,
    BoardColumnDetailView,
    BoardColumnReorderView,
)

app_name = "projects"

urlpatterns = [
    # Workspaces
    path(
        "workspaces/<uuid:pk>/",
        WorkspaceDetailView.as_view(),
        name="workspace-detail",
    ),
    path(
        "workspaces/<uuid:workspace_id>/projects/",
        ProjectListCreateView.as_view(),
        name="project-list-create",
    ),
    
    # Projects
    path(
        "projects/<uuid:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path(
        "projects/<uuid:pk>/members/",
        ProjectMemberListView.as_view(),
        name="project-member-list",
    ),
    path(
        "projects/<uuid:project_pk>/members/<uuid:member_pk>/",
        ProjectMemberDetailView.as_view(),
        name="project-member-detail",
    ),

    # Boards
    path(
        "projects/<uuid:pk>/boards/",
        BoardListCreateView.as_view(),
        name="board-list-create",
    ),
    path(
        "boards/<uuid:pk>/",
        BoardDetailView.as_view(),
        name="board-detail",
    ),

    # Board Columns
    path(
        "boards/<uuid:pk>/columns/",
        BoardColumnListCreateView.as_view(),
        name="column-list-create",
    ),
    path(
        "boards/<uuid:board_pk>/columns/<uuid:column_pk>/",
        BoardColumnDetailView.as_view(),
        name="column-detail",
    ),
    path(
        "boards/<uuid:pk>/columns/reorder/",
        BoardColumnReorderView.as_view(),
        name="column-reorder",
    ),
]

