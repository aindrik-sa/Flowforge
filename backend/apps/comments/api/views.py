from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.comments.models import Comment
from apps.comments.selectors import get_task_comments, get_comment_detail
from apps.comments.services import create_comment, update_comment, delete_comment
from apps.tasks.models import Task
from apps.tasks.permissions import IsTaskProjectMember, IsTaskProjectViewer
from apps.organizations.permissions import IsOrganizationAdmin
from .serializers import (
    CommentSerializer,
    CreateCommentSerializer,
    UpdateCommentSerializer,
)


class CommentListCreateView(APIView):
    """
    GET  /api/v1/tasks/<task_id>/comments/     — List top-level comments
    POST /api/v1/tasks/<task_id>/comments/     — Add a comment
    """

    def get_task(self, pk):
        try:
            return Task.objects.select_related(
                "project__workspace__organization"
            ).get(pk=pk)
        except Task.DoesNotExist:
            return None

    @extend_schema(responses={200: CommentSerializer(many=True)})
    def get(self, request, task_id):
        task = self.get_task(task_id)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectViewer().has_object_permission(request, self, task) and \
           not IsOrganizationAdmin().has_object_permission(request, self, task.project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        comments = get_task_comments(task=task)
        return Response(
            CommentSerializer(comments, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=CreateCommentSerializer,
        responses={201: CommentSerializer},
    )
    def post(self, request, task_id):
        task = self.get_task(task_id)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectMember().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent = None
        parent_id = serializer.validated_data.get("parent_id")
        if parent_id:
            try:
                parent = Comment.objects.get(pk=parent_id, task=task)
            except Comment.DoesNotExist:
                return Response(
                    {"detail": "Parent comment not found on this task."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if parent.parent_id is not None:
                return Response(
                    {"detail": "Cannot reply to a reply (max 1 level deep)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        comment = create_comment(
            task=task,
            author=request.user,
            body=serializer.validated_data["body"],
            parent=parent,
        )

        comment = get_comment_detail(comment_id=comment.id)
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class CommentDetailView(APIView):
    """
    PATCH  /api/v1/comments/<pk>/     — Update comment body
    DELETE /api/v1/comments/<pk>/     — Delete comment
    """

    def get_comment(self, pk):
        return get_comment_detail(comment_id=pk)

    @extend_schema(
        request=UpdateCommentSerializer,
        responses={200: CommentSerializer},
    )
    def patch(self, request, pk):
        comment = self.get_comment(pk)
        if not comment:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Only the author can edit their comment
        if comment.author_id != request.user.id:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = update_comment(
            comment=comment,
            body=serializer.validated_data["body"],
            updated_by=request.user,
        )

        comment = self.get_comment(pk)
        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        comment = self.get_comment(pk)
        if not comment:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Author can delete, or a project manager
        is_author = comment.author_id == request.user.id
        is_manager = IsTaskProjectMember().has_object_permission(request, self, comment.task)  # Actually should be manager? Let's check IsProjectManager
        from apps.projects.permissions import IsProjectManager
        is_project_manager = IsProjectManager().has_object_permission(request, self, comment.task.project)

        if not (is_author or is_project_manager):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        delete_comment(comment=comment)
        return Response(status=status.HTTP_204_NO_CONTENT)
