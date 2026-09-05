from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.organizations.models import Organization
from apps.organizations.permissions import IsOrganizationMember, IsOrganizationAdmin
from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn
from apps.projects.permissions import (
    IsWorkspaceManager,
    IsProjectManager,
    IsProjectMember,
    IsProjectViewer,
)
from apps.projects.selectors import (
    get_workspaces,
    get_projects,
    get_user_projects,
    get_project_members,
    get_boards,
    get_board_columns,
)
from apps.projects.services import (
    create_workspace,
    create_project,
    add_project_member,
    remove_project_member,
    change_project_member_role,
    create_board,
    create_board_column,
    reorder_columns,
    delete_board_column,
)
from .serializers import (
    WorkspaceSerializer,
    CreateWorkspaceSerializer,
    UpdateWorkspaceSerializer,
    ProjectSerializer,
    CreateProjectSerializer,
    UpdateProjectSerializer,
    ProjectMemberSerializer,
    AddProjectMemberSerializer,
    ChangeProjectMemberRoleSerializer,
    BoardSerializer,
    CreateBoardSerializer,
    UpdateBoardSerializer,
    BoardColumnSerializer,
    CreateBoardColumnSerializer,
    UpdateBoardColumnSerializer,
    ReorderColumnsSerializer,
)

User = get_user_model()


class WorkspaceListCreateView(APIView):
    """
    GET  /api/v1/organizations/<org_id>/workspaces/
    POST /api/v1/organizations/<org_id>/workspaces/
    """

    def get_organization(self, org_id):
        try:
            return Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return None

    @extend_schema(responses={200: WorkspaceSerializer(many=True)})
    def get(self, request, org_id):
        organization = self.get_organization(org_id)
        if not organization:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsOrganizationMember().has_object_permission(request, self, organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        workspaces = get_workspaces(organization=organization)
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CreateWorkspaceSerializer,
        responses={201: WorkspaceSerializer},
    )
    def post(self, request, org_id):
        organization = self.get_organization(org_id)
        if not organization:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsOrganizationAdmin().has_object_permission(request, self, organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateWorkspaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            workspace = create_workspace(
                organization=organization,
                **serializer.validated_data,
            )
        except IntegrityError:
            return Response(
                {"detail": "Workspace with this name or slug already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            WorkspaceSerializer(workspace).data,
            status=status.HTTP_201_CREATED,
        )


class WorkspaceDetailView(APIView):
    """
    GET    /api/v1/workspaces/<pk>/
    PATCH  /api/v1/workspaces/<pk>/
    DELETE /api/v1/workspaces/<pk>/
    """

    def get_object(self, pk):
        try:
            return Workspace.objects.select_related("organization").get(pk=pk)
        except Workspace.DoesNotExist:
            return None

    @extend_schema(responses={200: WorkspaceSerializer})
    def get(self, request, pk):
        workspace = self.get_object(pk)
        if not workspace:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsOrganizationMember().has_object_permission(request, self, workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        return Response(WorkspaceSerializer(workspace).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UpdateWorkspaceSerializer,
        responses={200: WorkspaceSerializer},
    )
    def patch(self, request, pk):
        workspace = self.get_object(pk)
        if not workspace:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsWorkspaceManager().has_object_permission(request, self, workspace):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateWorkspaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(workspace, field, value)
        
        try:
            workspace.save()
        except IntegrityError:
            return Response(
                {"detail": "Workspace with this name or slug already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(WorkspaceSerializer(workspace).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        workspace = self.get_object(pk)
        if not workspace:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsWorkspaceManager().has_object_permission(request, self, workspace):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        workspace.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectListCreateView(ListAPIView):
    """
    GET  /api/v1/workspaces/<workspace_id>/projects/
    POST /api/v1/workspaces/<workspace_id>/projects/
    """
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "created_by"]
    search_fields = ["name", "key", "description"]
    ordering_fields = ["created_at", "name", "start_date", "due_date"]
    ordering = ["-created_at"]

    def get_workspace(self, workspace_id):
        try:
            return Workspace.objects.select_related("organization").get(pk=workspace_id)
        except Workspace.DoesNotExist:
            return None

    def get_queryset(self):
        workspace_id = self.kwargs.get("workspace_id")
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return Project.objects.none()
        
        # If admin, can see all projects in workspace.
        # Otherwise, only projects they are a member of.
        # For simplicity in Sprint 3, and since IsOrganizationMember can view workspaces,
        # let's show all projects in the workspace if they are an org member,
        # or we restrict to what they are a member of? The PRD says "Users must only access workspaces belonging to organizations they are members of."
        # For projects: "List projects" -> let's list all in workspace if they have workspace access.
        if IsOrganizationMember().has_object_permission(self.request, self, workspace.organization):
             return get_projects(workspace=workspace)
        return Project.objects.none()

    def get(self, request, *args, **kwargs):
        workspace_id = self.kwargs.get("workspace_id")
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            
        if not IsOrganizationMember().has_object_permission(request, self, workspace.organization):
             return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=CreateProjectSerializer,
        responses={201: ProjectSerializer},
    )
    def post(self, request, workspace_id):
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsOrganizationMember().has_object_permission(request, self, workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        # Anyone in the organization can create a project in the workspace, 
        # or should it be restricted? The PRD just says "Create project". We'll let any org member create it.
        serializer = CreateProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            project = create_project(
                workspace=workspace,
                created_by=request.user,
                **serializer.validated_data,
            )
        except IntegrityError:
            return Response(
                {"detail": "Project with this key or slug already exists in this workspace."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_201_CREATED,
        )


class ProjectDetailView(APIView):
    """
    GET    /api/v1/projects/<pk>/
    PATCH  /api/v1/projects/<pk>/
    DELETE /api/v1/projects/<pk>/
    """

    def get_object(self, pk):
        try:
            return Project.objects.select_related("workspace__organization").get(pk=pk)
        except Project.DoesNotExist:
            return None

    @extend_schema(responses={200: ProjectSerializer})
    def get(self, request, pk):
        project = self.get_object(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectViewer().has_object_permission(request, self, project) and not IsOrganizationAdmin().has_object_permission(request, self, project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UpdateProjectSerializer,
        responses={200: ProjectSerializer},
    )
    def patch(self, request, pk):
        project = self.get_object(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(project, field, value)
            
        try:
            project.save()
        except IntegrityError:
            return Response(
                {"detail": "Project with this key or slug already exists in this workspace."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        project = self.get_object(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMemberListView(APIView):
    """
    GET  /api/v1/projects/<pk>/members/
    POST /api/v1/projects/<pk>/members/
    """
    
    def get_project(self, pk):
        try:
            return Project.objects.select_related("workspace__organization").get(pk=pk)
        except Project.DoesNotExist:
            return None

    @extend_schema(responses={200: ProjectMemberSerializer(many=True)})
    def get(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectViewer().has_object_permission(request, self, project) and not IsOrganizationAdmin().has_object_permission(request, self, project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        members = get_project_members(project=project)
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=AddProjectMemberSerializer,
        responses={201: ProjectMemberSerializer},
    )
    def post(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AddProjectMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])

        try:
            member = add_project_member(
                project=project,
                user=user,
                role=serializer.validated_data["role"],
            )
        except IntegrityError:
            return Response(
                {"detail": "User is already a member of this project."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            ProjectMemberSerializer(member).data,
            status=status.HTTP_201_CREATED,
        )


class ProjectMemberDetailView(APIView):
    """
    PATCH  /api/v1/projects/<project_pk>/members/<member_pk>/
    DELETE /api/v1/projects/<project_pk>/members/<member_pk>/
    """
    def get_project(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    def get_member(self, pk):
        try:
            return ProjectMember.objects.select_related("user").get(pk=pk)
        except ProjectMember.DoesNotExist:
            return None

    @extend_schema(
        request=ChangeProjectMemberRoleSerializer,
        responses={200: ProjectMemberSerializer},
    )
    def patch(self, request, project_pk, member_pk):
        project = self.get_project(project_pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        member = self.get_member(member_pk)
        if not member or member.project_id != project.id:
             return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChangeProjectMemberRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_member = change_project_member_role(
                project=project,
                user=member.user,
                new_role=serializer.validated_data["role"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ProjectMemberSerializer(updated_member).data, status=status.HTTP_200_OK)

    def delete(self, request, project_pk, member_pk):
        project = self.get_project(project_pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        member = self.get_member(member_pk)
        if not member or member.project_id != project.id:
             return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            remove_project_member(
                project=project,
                user=member.user,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Board Views
# ---------------------------------------------------------------------------


class BoardListCreateView(APIView):
    """
    GET  /api/v1/projects/<pk>/boards/     — List boards for a project
    POST /api/v1/projects/<pk>/boards/     — Create a new board

    Permissions:
    - GET: any organization member (via project's org)
    - POST: project managers only
    """

    def get_project(self, pk):
        try:
            return Project.objects.select_related("workspace__organization").get(pk=pk)
        except Project.DoesNotExist:
            return None

    @extend_schema(responses={200: BoardSerializer(many=True)})
    def get(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectViewer().has_object_permission(request, self, project) and \
           not IsOrganizationAdmin().has_object_permission(request, self, project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        boards = get_boards(project=project)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CreateBoardSerializer,
        responses={201: BoardSerializer},
    )
    def post(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateBoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            board = create_board(
                project=project,
                **serializer.validated_data,
            )
        except IntegrityError:
            return Response(
                {"detail": "Board with this slug already exists in this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            BoardSerializer(board).data,
            status=status.HTTP_201_CREATED,
        )


class BoardDetailView(APIView):
    """
    GET    /api/v1/boards/<pk>/    — Retrieve board with columns
    PATCH  /api/v1/boards/<pk>/    — Update board
    DELETE /api/v1/boards/<pk>/    — Delete board

    Permissions:
    - GET: project viewer or org admin
    - PATCH/DELETE: project manager only
    """

    def get_object(self, pk):
        try:
            return Board.objects.select_related(
                "project__workspace__organization"
            ).prefetch_related("columns").get(pk=pk)
        except Board.DoesNotExist:
            return None

    @extend_schema(responses={200: BoardSerializer})
    def get(self, request, pk):
        board = self.get_object(pk)
        if not board:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        project = board.project
        if not IsProjectViewer().has_object_permission(request, self, project) and \
           not IsOrganizationAdmin().has_object_permission(request, self, project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        return Response(BoardSerializer(board).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UpdateBoardSerializer,
        responses={200: BoardSerializer},
    )
    def patch(self, request, pk):
        board = self.get_object(pk)
        if not board:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, board.project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateBoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Handle is_default promotion — demote others first
        if serializer.validated_data.get("is_default", False):
            Board.objects.filter(
                project=board.project, is_default=True
            ).exclude(pk=board.pk).update(is_default=False)

        for field, value in serializer.validated_data.items():
            setattr(board, field, value)

        try:
            board.save()
        except IntegrityError:
            return Response(
                {"detail": "Board with this slug already exists in this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Re-fetch to include updated columns
        board = self.get_object(pk)
        return Response(BoardSerializer(board).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        board = self.get_object(pk)
        if not board:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, board.project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        # Prevent deleting the last board
        board_count = Board.objects.filter(project=board.project).count()
        if board_count <= 1:
            return Response(
                {"detail": "Cannot delete the only board in a project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardColumnListCreateView(APIView):
    """
    GET  /api/v1/boards/<pk>/columns/     — List columns for a board
    POST /api/v1/boards/<pk>/columns/     — Add a column

    Permissions:
    - GET: project viewer or org admin
    - POST: project manager only
    """

    def get_board(self, pk):
        try:
            return Board.objects.select_related(
                "project__workspace__organization"
            ).get(pk=pk)
        except Board.DoesNotExist:
            return None

    @extend_schema(responses={200: BoardColumnSerializer(many=True)})
    def get(self, request, pk):
        board = self.get_board(pk)
        if not board:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        project = board.project
        if not IsProjectViewer().has_object_permission(request, self, project) and \
           not IsOrganizationAdmin().has_object_permission(request, self, project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        columns = get_board_columns(board=board)
        serializer = BoardColumnSerializer(columns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CreateBoardColumnSerializer,
        responses={201: BoardColumnSerializer},
    )
    def post(self, request, pk):
        board = self.get_board(pk)
        if not board:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, board.project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateBoardColumnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            column = create_board_column(
                board=board,
                **serializer.validated_data,
            )
        except IntegrityError:
            return Response(
                {"detail": "Column with this slug already exists in this board."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            BoardColumnSerializer(column).data,
            status=status.HTTP_201_CREATED,
        )


class BoardColumnDetailView(APIView):
    """
    PATCH  /api/v1/boards/<board_pk>/columns/<column_pk>/  — Update column
    DELETE /api/v1/boards/<board_pk>/columns/<column_pk>/  — Remove column
    """

    def get_board(self, pk):
        try:
            return Board.objects.select_related(
                "project__workspace__organization"
            ).get(pk=pk)
        except Board.DoesNotExist:
            return None

    def get_column(self, pk):
        try:
            return BoardColumn.objects.get(pk=pk)
        except BoardColumn.DoesNotExist:
            return None

    @extend_schema(
        request=UpdateBoardColumnSerializer,
        responses={200: BoardColumnSerializer},
    )
    def patch(self, request, board_pk, column_pk):
        board = self.get_board(board_pk)
        if not board:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, board.project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        column = self.get_column(column_pk)
        if not column or column.board_id != board.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateBoardColumnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(column, field, value)

        try:
            column.save()
        except IntegrityError:
            return Response(
                {"detail": "Column update failed due to a conflict."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(BoardColumnSerializer(column).data, status=status.HTTP_200_OK)

    def delete(self, request, board_pk, column_pk):
        board = self.get_board(board_pk)
        if not board:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, board.project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        column = self.get_column(column_pk)
        if not column or column.board_id != board.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        delete_board_column(column=column)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardColumnReorderView(APIView):
    """
    POST /api/v1/boards/<pk>/columns/reorder/

    Reorder columns within a board by providing the full list of
    column IDs in the desired order.

    Permissions: project manager only
    """

    def get_board(self, pk):
        try:
            return Board.objects.select_related(
                "project__workspace__organization"
            ).get(pk=pk)
        except Board.DoesNotExist:
            return None

    @extend_schema(
        request=ReorderColumnsSerializer,
        responses={200: BoardColumnSerializer(many=True)},
    )
    def post(self, request, pk):
        board = self.get_board(pk)
        if not board:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsProjectManager().has_object_permission(request, self, board.project):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReorderColumnsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reorder_columns(
                board=board,
                ordered_column_ids=serializer.validated_data["ordered_column_ids"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Return the updated column order
        columns = get_board_columns(board=board)
        return Response(
            BoardColumnSerializer(columns, many=True).data,
            status=status.HTTP_200_OK,
        )

