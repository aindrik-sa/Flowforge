from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.reports.services import get_project_dashboard_stats, get_user_productivity_stats
from apps.projects.permissions import IsProjectMember


class ProjectDashboardAPI(APIView):
    """
    GET /api/v1/projects/<project_id>/dashboard/
    Return aggregated statistics for a project.
    """
    permission_classes = [IsAuthenticated, IsProjectMember]

    def get(self, request, project_id):
        try:
            stats = get_project_dashboard_stats(project_id=project_id)
            return Response(stats, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class UserProductivityAPI(APIView):
    """
    GET /api/v1/users/<user_id>/productivity/
    Return productivity statistics for a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Users can only view their own productivity for privacy, unless they are admins.
        # Simple check for now:
        if str(request.user.id) != str(user_id) and not request.user.is_superuser:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
            
        stats = get_user_productivity_stats(user_id=user_id)
        return Response(stats, status=status.HTTP_200_OK)
