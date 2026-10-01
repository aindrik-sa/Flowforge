from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.notifications.models import Notification
from apps.notifications.services import mark_as_read, mark_all_as_read
from .serializers import NotificationSerializer


class NotificationListView(ListAPIView):
    """
    GET /api/v1/notifications/
    List notifications for the current authenticated user.
    """
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["is_read"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related("actor")


class NotificationReadView(APIView):
    """
    POST /api/v1/notifications/<pk>/read/
    Mark a single notification as read.
    """
    @extend_schema(responses={200: NotificationSerializer})
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        notification = mark_as_read(notification=notification)
        return Response(NotificationSerializer(notification).data, status=status.HTTP_200_OK)


class NotificationReadAllView(APIView):
    """
    POST /api/v1/notifications/read-all/
    Mark all unread notifications as read.
    """
    def post(self, request):
        mark_all_as_read(user=request.user)
        return Response({"detail": "All notifications marked as read."}, status=status.HTTP_200_OK)
