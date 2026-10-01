from django.urls import path

from .views import (
    TaskListCreateView,
    TaskDetailView,
    TaskMoveView,
    TaskReorderView,
    TaskAssignmentListView,
    TaskAssignmentDetailView,
    TaskLabelListCreateView,
    TaskLabelDetailView,
    TaskLabelManageView,
    TaskLabelRemoveView,
    TaskActivityView,
)

app_name = "tasks"

urlpatterns = [
    # Tasks scoped to a project
    path(
        "projects/<uuid:pk>/tasks/",
        TaskListCreateView.as_view(),
        name="task-list-create",
    ),

    # Task detail (CRUD)
    path(
        "tasks/<uuid:pk>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),

    # Task movement between columns
    path(
        "tasks/<uuid:pk>/move/",
        TaskMoveView.as_view(),
        name="task-move",
    ),

    # Reorder tasks within a column
    path(
        "columns/<uuid:pk>/tasks/reorder/",
        TaskReorderView.as_view(),
        name="task-reorder",
    ),

    # Task assignments
    path(
        "tasks/<uuid:pk>/assignees/",
        TaskAssignmentListView.as_view(),
        name="task-assignment-list",
    ),
    path(
        "tasks/<uuid:task_pk>/assignees/<uuid:assignment_pk>/",
        TaskAssignmentDetailView.as_view(),
        name="task-assignment-detail",
    ),

    # Labels scoped to a project
    path(
        "projects/<uuid:pk>/labels/",
        TaskLabelListCreateView.as_view(),
        name="label-list-create",
    ),
    path(
        "projects/<uuid:project_pk>/labels/<uuid:label_pk>/",
        TaskLabelDetailView.as_view(),
        name="label-detail",
    ),

    # Labels on a task
    path(
        "tasks/<uuid:pk>/labels/",
        TaskLabelManageView.as_view(),
        name="task-label-add",
    ),
    path(
        "tasks/<uuid:task_pk>/labels/<uuid:label_pk>/",
        TaskLabelRemoveView.as_view(),
        name="task-label-remove",
    ),

    # Activity log
    path(
        "tasks/<uuid:pk>/activity/",
        TaskActivityView.as_view(),
        name="task-activity",
    ),
]
