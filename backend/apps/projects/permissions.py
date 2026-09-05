from rest_framework.permissions import BasePermission

from apps.projects.models import ProjectMember
from apps.organizations.permissions import IsOrganizationMember, IsOrganizationAdmin


class IsWorkspaceManager(BasePermission):
    """
    Allows access to Workspace-level operations.
    Currently, relies on Organization Admin permissions.
    """

    def has_object_permission(self, request, view, obj):
        org_admin_permission = IsOrganizationAdmin()
        return org_admin_permission.has_object_permission(request, view, obj.organization)


class IsProjectManager(BasePermission):
    """
    Allows access only to project managers.
    """

    def has_object_permission(self, request, view, obj):
        return ProjectMember.objects.filter(
            project=obj,
            user=request.user,
            role=ProjectMember.Role.MANAGER,
        ).exists()


class IsProjectMember(BasePermission):
    """
    Allows access to project members and managers (excludes viewers for write operations).
    """

    def has_object_permission(self, request, view, obj):
        return ProjectMember.objects.filter(
            project=obj,
            user=request.user,
            role__in=[ProjectMember.Role.MANAGER, ProjectMember.Role.MEMBER],
        ).exists()


class IsProjectViewer(BasePermission):
    """
    Allows read-only access to anyone who is a member of the project in any capacity.
    """

    def has_object_permission(self, request, view, obj):
        return ProjectMember.objects.filter(
            project=obj,
            user=request.user,
        ).exists()
