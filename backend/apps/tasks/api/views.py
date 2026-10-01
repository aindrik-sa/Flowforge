from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.projects.models import Project, ProjectMember, BoardColumn
from apps.projects.permissions import (
    IsProjectManager,
    IsProjectMember,
    IsProjectViewer,
)
from apps.organizations.permissions import IsOrganizationAdmin
from apps.tasks.models import Task, TaskLabel, TaskAssignment
from apps.tasks.permissions import (
    IsTaskProjectMember,
    IsTaskProjectManager,
    IsTaskProjectViewer,
)
from apps.tasks.selectors import (
    get_project_tasks,
    get_task_detail,
    get_task_assignments,
    get_task_activity,
    get_project_labels,
)
from apps.tasks.services import (
    create_task,
    update_task,
    move_task,
    reorder_tasks,
    assign_task,
    unassign_task,
    create_label,
    add_label_to_task,
    remove_label_from_task,
)
from .serializers import (
    TaskSerializer,
    TaskListSerializer,
    CreateTaskSerializer,
    UpdateTaskSerializer,
    MoveTaskSerializer,
    ReorderTasksSerializer,
    TaskAssignmentSerializer,
    AssignTaskSerializer,
    TaskLabelSerializer,
    CreateTaskLabelSerializer,
    AddLabelToTaskSerializer,
    TaskActivityLogSerializer,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------


class TaskListCreateView(ListAPIView):
    """
    GET  /api/v1/projects/<pk>/tasks/     — List tasks in a project
    POST /api/v1/projects/<pk>/tasks/     — Create a task

    Supports filtering by priority, column, and assignee.
    Supports search on title and description.
    """

    serializer_class = TaskListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["priority", "column"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "task_number", "priority", "due_date", "position"]
    ordering = ["column__position", "position"]

    def get_project(self, pk):
        try:
            return Project.objects.select_related("workspace__organization").get(pk=pk)
        except Project.DoesNotExist:
            return None

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        project = self.get_project(pk)
        if not project:
            return Task.objects.none()

        if IsProjectViewer().has_object_permission(self.request, self, project) or \
           IsOrganizationAdmin().has_object_permission(self.request, self, project.workspace.organization):
            return get_project_tasks(project=project)
        return Task.objects.none()

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        project = self.get_project(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectViewer().has_object_permission(request, self, project) and \
           not IsOrganizationAdmin().has_object_permission(request, self, project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=CreateTaskSerializer,
        responses={201: TaskSerializer},
    )
    def post(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectMember().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate that the column belongs to this project
        column_id = serializer.validated_data.pop("column_id")
        try:
            column = BoardColumn.objects.select_related("board__project").get(pk=column_id)
        except BoardColumn.DoesNotExist:
            return Response(
                {"detail": "Column not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if column.board.project_id != project.id:
            return Response(
                {"detail": "Column does not belong to this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = create_task(
                project=project,
                column=column,
                created_by=request.user,
                **serializer.validated_data,
            )
        except IntegrityError:
            return Response(
                {"detail": "Task creation failed due to a conflict."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Re-fetch with prefetched relations
        task = get_task_detail(task_id=task.id)
        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_201_CREATED,
        )


class TaskDetailView(APIView):
    """
    GET    /api/v1/tasks/<pk>/     — Retrieve task
    PATCH  /api/v1/tasks/<pk>/     — Update task
    DELETE /api/v1/tasks/<pk>/     — Delete task
    """

    def get_object(self, pk):
        return get_task_detail(task_id=pk)

    @extend_schema(responses={200: TaskSerializer})
    def get(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectViewer().has_object_permission(request, self, task) and \
           not IsOrganizationAdmin().has_object_permission(request, self, task.project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UpdateTaskSerializer,
        responses={200: TaskSerializer},
    )
    def patch(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectMember().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = update_task(
            task=task,
            updated_by=request.user,
            **serializer.validated_data,
        )

        # Re-fetch with full relations
        task = self.get_object(pk)
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectManager().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Task Movement
# ---------------------------------------------------------------------------


class TaskMoveView(APIView):
    """
    POST /api/v1/tasks/<pk>/move/   — Move task to a different column/position
    """

    def get_object(self, pk):
        return get_task_detail(task_id=pk)

    @extend_schema(
        request=MoveTaskSerializer,
        responses={200: TaskSerializer},
    )
    def post(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectMember().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MoveTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        column_id = serializer.validated_data["column_id"]
        try:
            target_column = BoardColumn.objects.select_related("board__project").get(pk=column_id)
        except BoardColumn.DoesNotExist:
            return Response(
                {"detail": "Target column not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if target_column.board.project_id != task.project_id:
            return Response(
                {"detail": "Target column does not belong to this task's project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = move_task(
            task=task,
            target_column=target_column,
            position=serializer.validated_data.get("position"),
            moved_by=request.user,
        )

        task = self.get_object(pk)
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)


class TaskReorderView(APIView):
    """
    POST /api/v1/columns/<pk>/tasks/reorder/

    Reorder tasks within a column by providing the full list of
    task IDs in the desired order.
    """

    def get_column(self, pk):
        try:
            return BoardColumn.objects.select_related(
                "board__project__workspace__organization"
            ).get(pk=pk)
        except BoardColumn.DoesNotExist:
            return None

    @extend_schema(
        request=ReorderTasksSerializer,
        responses={200: TaskListSerializer(many=True)},
    )
    def post(self, request, pk):
        column = self.get_column(pk)
        if not column:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        project = column.board.project
        if not IsProjectMember().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReorderTasksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reorder_tasks(
                column=column,
                ordered_task_ids=serializer.validated_data["ordered_task_ids"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        from apps.tasks.selectors import get_column_tasks
        tasks = get_column_tasks(column=column)
        return Response(
            TaskListSerializer(tasks, many=True).data,
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Task Assignments
# ---------------------------------------------------------------------------


class TaskAssignmentListView(APIView):
    """
    GET  /api/v1/tasks/<pk>/assignees/     — List assignees
    POST /api/v1/tasks/<pk>/assignees/     — Assign a user
    """

    def get_task(self, pk):
        return get_task_detail(task_id=pk)

    @extend_schema(responses={200: TaskAssignmentSerializer(many=True)})
    def get(self, request, pk):
        task = self.get_task(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectViewer().has_object_permission(request, self, task) and \
           not IsOrganizationAdmin().has_object_permission(request, self, task.project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        assignments = get_task_assignments(task=task)
        return Response(
            TaskAssignmentSerializer(assignments, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=AssignTaskSerializer,
        responses={201: TaskAssignmentSerializer},
    )
    def post(self, request, pk):
        task = self.get_task(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectMember().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AssignTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])

        try:
            assignment = assign_task(
                task=task,
                user=user,
                assigned_by=request.user,
            )
        except IntegrityError:
            return Response(
                {"detail": "User is already assigned to this task."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            TaskAssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )


class TaskAssignmentDetailView(APIView):
    """
    DELETE /api/v1/tasks/<task_pk>/assignees/<assignment_pk>/
    """

    def get_task(self, pk):
        return get_task_detail(task_id=pk)

    def delete(self, request, task_pk, assignment_pk):
        task = self.get_task(task_pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectMember().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        try:
            assignment = TaskAssignment.objects.select_related("user").get(pk=assignment_pk)
        except TaskAssignment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if assignment.task_id != task.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            unassign_task(
                task=task,
                user=assignment.user,
                removed_by=request.user,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Task Labels
# ---------------------------------------------------------------------------


class TaskLabelListCreateView(APIView):
    """
    GET  /api/v1/projects/<pk>/labels/     — List project labels
    POST /api/v1/projects/<pk>/labels/     — Create a label
    """

    def get_project(self, pk):
        try:
            return Project.objects.select_related("workspace__organization").get(pk=pk)
        except Project.DoesNotExist:
            return None

    @extend_schema(responses={200: TaskLabelSerializer(many=True)})
    def get(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectViewer().has_object_permission(request, self, project) and \
           not IsOrganizationAdmin().has_object_permission(request, self, project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        labels = get_project_labels(project=project)
        return Response(
            TaskLabelSerializer(labels, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=CreateTaskLabelSerializer,
        responses={201: TaskLabelSerializer},
    )
    def post(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateTaskLabelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            label = create_label(
                project=project,
                **serializer.validated_data,
            )
        except IntegrityError:
            return Response(
                {"detail": "A label with this name already exists in the project."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            TaskLabelSerializer(label).data,
            status=status.HTTP_201_CREATED,
        )


class TaskLabelDetailView(APIView):
    """
    DELETE /api/v1/projects/<project_pk>/labels/<label_pk>/
    """

    def get_project(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    def delete(self, request, project_pk, label_pk):
        project = self.get_project(project_pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        try:
            label = TaskLabel.objects.get(pk=label_pk, project=project)
        except TaskLabel.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        label.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskLabelManageView(APIView):
    """
    POST   /api/v1/tasks/<pk>/labels/         — Add a label to a task
    DELETE /api/v1/tasks/<task_pk>/labels/<label_pk>/  — Remove a label from a task
    """

    def get_task(self, pk):
        return get_task_detail(task_id=pk)

    @extend_schema(
        request=AddLabelToTaskSerializer,
        responses={200: TaskSerializer},
    )
    def post(self, request, pk):
        task = self.get_task(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectMember().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AddLabelToTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            label = TaskLabel.objects.get(
                pk=serializer.validated_data["label_id"],
                project=task.project,
            )
        except TaskLabel.DoesNotExist:
            return Response(
                {"detail": "Label not found in this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        add_label_to_task(task=task, label=label, added_by=request.user)

        task = self.get_task(pk)
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)


class TaskLabelRemoveView(APIView):
    """
    DELETE /api/v1/tasks/<task_pk>/labels/<label_pk>/
    """

    def get_task(self, pk):
        return get_task_detail(task_id=pk)

    def delete(self, request, task_pk, label_pk):
        task = self.get_task(task_pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectMember().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        try:
            label = TaskLabel.objects.get(pk=label_pk, project=task.project)
        except TaskLabel.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        remove_label_from_task(task=task, label=label, removed_by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Activity Log
# ---------------------------------------------------------------------------


class TaskActivityView(APIView):
    """
    GET /api/v1/tasks/<pk>/activity/   — View task activity log
    """

    def get_task(self, pk):
        return get_task_detail(task_id=pk)

    @extend_schema(responses={200: TaskActivityLogSerializer(many=True)})
    def get(self, request, pk):
        task = self.get_task(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectViewer().has_object_permission(request, self, task) and \
           not IsOrganizationAdmin().has_object_permission(request, self, task.project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        activity = get_task_activity(task=task)
        return Response(
            TaskActivityLogSerializer(activity, many=True).data,
            status=status.HTTP_200_OK,
        )
