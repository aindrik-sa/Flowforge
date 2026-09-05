"""
Tests for Organization and OrganizationMember models.
"""
import pytest
from django.db import IntegrityError

from apps.organizations.models import Organization, OrganizationMember


@pytest.mark.django_db
class TestOrganizationModel:
    def test_organization_creation(self, user):
        org = Organization.objects.create(name="Test Org", owner=user)
        assert org.name == "Test Org"
        assert org.slug == "test-org"  # Automatically slugified
        assert org.owner == user
        assert org.id is not None
        assert str(org) == "Test Org"


@pytest.mark.django_db
class TestOrganizationMemberModel:
    def test_member_creation(self, user, create_user):
        org = Organization.objects.create(name="Test Org", owner=user)
        member_user = create_user(email="member@example.com")
        
        member = OrganizationMember.objects.create(
            organization=org,
            user=member_user,
            role=OrganizationMember.Role.ADMIN,
        )
        
        assert member.organization == org
        assert member.user == member_user
        assert member.role == OrganizationMember.Role.ADMIN
        assert str(member) == f"member@example.com → Test Org (admin)"

    def test_unique_organization_member(self, user, create_user):
        """A user cannot have multiple memberships in the same organization."""
        org = Organization.objects.create(name="Test Org", owner=user)
        member_user = create_user(email="member@example.com")
        
        OrganizationMember.objects.create(
            organization=org,
            user=member_user,
            role=OrganizationMember.Role.ADMIN,
        )
        
        with pytest.raises(IntegrityError):
            OrganizationMember.objects.create(
                organization=org,
                user=member_user,
                role=OrganizationMember.Role.MEMBER,
            )
