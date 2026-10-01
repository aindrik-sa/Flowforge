from rest_framework.permissions import BasePermission

from apps.projects.models import ProjectMember


class IsTaskProjectMember(BasePermission):
    """
    Allows access to users who are a member or manager of the task's project.
    Expects `obj` to be a Task instance.
    """

    def has_object_permission(self, request, view, obj):
        return ProjectMember.objects.filter(
            project=obj.project,
            user=request.user,
            role__in=[ProjectMember.Role.MANAGER, ProjectMember.Role.MEMBER],
        ).exists()


class IsTaskProjectManager(BasePermission):
    """
    Allows access only to managers of the task's project.
    Expects `obj` to be a Task instance.
    """

    def has_object_permission(self, request, view, obj):
        return ProjectMember.objects.filter(
            project=obj.project,
            user=request.user,
            role=ProjectMember.Role.MANAGER,
        ).exists()


class IsTaskProjectViewer(BasePermission):
    """
    Allows read-only access to anyone who is a member of the task's
    project in any capacity (including viewers).
    Expects `obj` to be a Task instance.
    """

    def has_object_permission(self, request, view, obj):
        return ProjectMember.objects.filter(
            project=obj.project,
            user=request.user,
        ).exists()
