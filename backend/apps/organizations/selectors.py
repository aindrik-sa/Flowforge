from apps.organizations.models import Organization, OrganizationMember


def get_user_organizations(*, user):
    """
    Return all organizations the user is a member of.

    WHAT: Selector that returns only organizations the user belongs to.
    WHY:  Centralized query logic prevents accidental data leakage.
          Every view that lists organizations uses this selector.
    IMPORTANT: This is the ONLY way to list organizations for a user.
               Never do Organization.objects.all() in a view.
    """
    return Organization.objects.filter(
        members__user=user,
    ).select_related("owner").distinct()


def get_organization_members(*, organization: Organization):
    """
    Return all members of an organization with user details.
    Uses select_related to prevent N+1 queries on user.
    """
    return OrganizationMember.objects.filter(
        organization=organization,
    ).select_related("user")


def get_user_membership(*, organization: Organization, user):
    """
    Get a specific user's membership in an organization.
    Returns None if the user is not a member.
    """
    return OrganizationMember.objects.filter(
        organization=organization,
        user=user,
    ).select_related("user").first()
