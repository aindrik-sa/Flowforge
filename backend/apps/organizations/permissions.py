from rest_framework.permissions import BasePermission

from apps.organizations.models import OrganizationMember


class IsOrganizationMember(BasePermission):
    """
    Allows access only to members of the organization.

    WHAT: Checks that the requesting user is a member of the organization
          identified by the 'pk' in the URL.
    WHY:  Tenant isolation — users must not access organizations they
          don't belong to. This is the base permission for all org endpoints.
    IMPORTANT: This permission is checked AFTER authentication. An
               unauthenticated request is handled by IsAuthenticated first.
    """

    def has_object_permission(self, request, view, obj):
        return OrganizationMember.objects.filter(
            organization=obj,
            user=request.user,
        ).exists()


class IsOrganizationAdmin(BasePermission):
    """
    Allows access only to admins and owners of the organization.
    Used for sensitive operations like managing members and settings.
    """

    def has_object_permission(self, request, view, obj):
        return OrganizationMember.objects.filter(
            organization=obj,
            user=request.user,
            role__in=[
                OrganizationMember.Role.OWNER,
                OrganizationMember.Role.ADMIN,
            ],
        ).exists()


class IsOrganizationOwner(BasePermission):
    """
    Allows access only to the owner of the organization.
    Used for destructive operations like deleting the organization.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
