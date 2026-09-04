from django.db import transaction
from django.utils.text import slugify

from apps.organizations.models import Organization, OrganizationMember


def create_organization(
    *,
    name: str,
    owner,
    description: str = "",
    slug: str = "",
) -> Organization:
    """
    Create a new organization and add the creator as an owner member.

    WHAT: Atomic operation — creates org + membership in one transaction.
    WHY:  An organization without an owner member is a broken state.
          Using a transaction ensures both succeed or both fail.
    IMPORTANT: Always use this service instead of Organization.objects.create()
               to ensure the owner membership is created automatically.
    """
    if not slug:
        slug = slugify(name)

    # Ensure slug uniqueness by appending a suffix if needed
    base_slug = slug
    counter = 1
    while Organization.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    with transaction.atomic():
        organization = Organization.objects.create(
            name=name,
            slug=slug,
            description=description,
            owner=owner,
        )

        OrganizationMember.objects.create(
            organization=organization,
            user=owner,
            role=OrganizationMember.Role.OWNER,
        )

    return organization


def add_member(
    *,
    organization: Organization,
    user,
    role: str = OrganizationMember.Role.MEMBER,
) -> OrganizationMember:
    """
    Add a user to an organization with the specified role.

    Raises IntegrityError if the user is already a member.
    """
    member = OrganizationMember.objects.create(
        organization=organization,
        user=user,
        role=role,
    )
    return member


def remove_member(
    *,
    organization: Organization,
    user,
) -> None:
    """
    Remove a user from an organization.

    IMPORTANT: The organization owner cannot be removed.
    """
    if organization.owner == user:
        raise ValueError("Cannot remove the organization owner.")

    membership = OrganizationMember.objects.filter(
        organization=organization,
        user=user,
    )
    deleted_count, _ = membership.delete()

    if deleted_count == 0:
        raise ValueError("User is not a member of this organization.")


def change_member_role(
    *,
    organization: Organization,
    user,
    new_role: str,
) -> OrganizationMember:
    """
    Change a member's role within an organization.

    IMPORTANT: Cannot change the owner's role. To transfer ownership,
    a separate operation would be needed (future feature).
    """
    if organization.owner == user and new_role != OrganizationMember.Role.OWNER:
        raise ValueError("Cannot change the organization owner's role.")

    try:
        membership = OrganizationMember.objects.get(
            organization=organization,
            user=user,
        )
    except OrganizationMember.DoesNotExist:
        raise ValueError("User is not a member of this organization.")

    membership.role = new_role
    membership.save(update_fields=["role", "updated_at"])
    return membership
