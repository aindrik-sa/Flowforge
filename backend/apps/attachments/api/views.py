from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from apps.attachments.models import Attachment
from apps.attachments.selectors import get_task_attachments, get_attachment_detail
from apps.attachments.services import create_attachment, delete_attachment
from apps.tasks.models import Task
from apps.tasks.permissions import IsTaskProjectMember, IsTaskProjectViewer
from apps.organizations.permissions import IsOrganizationAdmin
from .serializers import AttachmentSerializer, UploadAttachmentSerializer


class AttachmentListCreateView(APIView):
    """
    GET  /api/v1/tasks/<task_id>/attachments/     — List attachments
    POST /api/v1/tasks/<task_id>/attachments/     — Upload attachment
    """
    parser_classes = (MultiPartParser, FormParser)

    def get_task(self, pk):
        try:
            return Task.objects.select_related(
                "project__workspace__organization"
            ).get(pk=pk)
        except Task.DoesNotExist:
            return None

    @extend_schema(responses={200: AttachmentSerializer(many=True)})
    def get(self, request, task_id):
        task = self.get_task(task_id)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectViewer().has_object_permission(request, self, task) and \
           not IsOrganizationAdmin().has_object_permission(request, self, task.project.workspace.organization):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        attachments = get_task_attachments(task=task)
        serializer = AttachmentSerializer(attachments, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UploadAttachmentSerializer,
        responses={201: AttachmentSerializer},
    )
    def post(self, request, task_id):
        task = self.get_task(task_id)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not IsTaskProjectMember().has_object_permission(request, self, task):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UploadAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = create_attachment(
                task=task,
                file=serializer.validated_data["file"],
                uploaded_by=request.user,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attachment = get_attachment_detail(attachment_id=attachment.id)
        return Response(
            AttachmentSerializer(attachment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AttachmentDetailView(APIView):
    """
    DELETE /api/v1/attachments/<pk>/     — Delete attachment
    """

    def get_attachment(self, pk):
        return get_attachment_detail(attachment_id=pk)

    def delete(self, request, pk):
        attachment = self.get_attachment(pk)
        if not attachment:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Author can delete, or a project manager
        is_uploader = attachment.uploaded_by_id == request.user.id
        from apps.projects.permissions import IsProjectManager
        is_project_manager = IsProjectManager().has_object_permission(request, self, attachment.task.project)

        if not (is_uploader or is_project_manager):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        delete_attachment(attachment=attachment)
        return Response(status=status.HTTP_204_NO_CONTENT)
