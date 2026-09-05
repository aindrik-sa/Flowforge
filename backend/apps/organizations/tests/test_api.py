"""
Tests for Organization API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.organizations.models import Organization, OrganizationMember
from apps.organizations.services import create_organization


@pytest.mark.django_db
class TestOrganizationAPI:
    def test_list_organizations(self, authenticated_client, user, create_user):
        """User should only see organizations they belong to."""
        # Org 1: User is owner
        create_organization(name="Org 1", owner=user)
        
        # Org 2: User is member
        org2_owner = create_user(email="owner2@example.com")
        org2 = create_organization(name="Org 2", owner=org2_owner)
        OrganizationMember.objects.create(
            organization=org2, user=user, role=OrganizationMember.Role.MEMBER
        )
        
        # Org 3: User is NOT a member
        org3_owner = create_user(email="owner3@example.com")
        create_organization(name="Org 3", owner=org3_owner)
        
        url = reverse("organizations:list-create")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        names = [org["name"] for org in response.data]
        assert "Org 1" in names
        assert "Org 2" in names
        assert "Org 3" not in names

    def test_create_organization(self, authenticated_client, user):
        """User can create an organization and becomes owner automatically."""
        url = reverse("organizations:list-create")
        data = {"name": "New Startup"}
        
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Startup"
        
        org_id = response.data["id"]
        # Check membership was created
        membership = OrganizationMember.objects.get(
            organization_id=org_id, user=user
        )
        assert membership.role == OrganizationMember.Role.OWNER

    def test_retrieve_organization(self, authenticated_client, user):
        org = create_organization(name="My Org", owner=user)
        url = reverse("organizations:detail", kwargs={"pk": org.id})
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "My Org"

    def test_update_organization_admin(self, authenticated_client, user):
        """Owner can update organization details."""
        org = create_organization(name="Old Name", owner=user)
        url = reverse("organizations:detail", kwargs={"pk": org.id})
        
        response = authenticated_client.patch(url, {"name": "New Name"})
        assert response.status_code == status.HTTP_200_OK
        
        org.refresh_from_db()
        assert org.name == "New Name"

    def test_update_organization_member_forbidden(self, authenticated_client, user, create_user):
        """Regular member cannot update organization details."""
        owner = create_user(email="owner@example.com")
        org = create_organization(name="Org", owner=owner)
        OrganizationMember.objects.create(
            organization=org, user=user, role=OrganizationMember.Role.MEMBER
        )
        
        url = reverse("organizations:detail", kwargs={"pk": org.id})
        response = authenticated_client.patch(url, {"name": "Hacked Name"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_organization_owner(self, authenticated_client, user):
        """Owner can delete the organization."""
        org = create_organization(name="To Delete", owner=user)
        url = reverse("organizations:detail", kwargs={"pk": org.id})
        
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Organization.objects.filter(id=org.id).exists()


@pytest.mark.django_db
class TestOrganizationMemberAPI:
    def test_list_members(self, authenticated_client, user, create_user):
        org = create_organization(name="My Org", owner=user)
        member2 = create_user(email="m2@example.com")
        OrganizationMember.objects.create(
            organization=org, user=member2, role=OrganizationMember.Role.MEMBER
        )
        
        url = reverse("organizations:member-list", kwargs={"pk": org.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_add_member(self, authenticated_client, user, create_user):
        org = create_organization(name="My Org", owner=user)
        new_user = create_user(email="new@example.com")
        
        url = reverse("organizations:member-list", kwargs={"pk": org.id})
        data = {"email": "new@example.com", "role": "manager"}
        
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["email"] == "new@example.com"
        assert response.data["role"] == "manager"

    def test_change_member_role(self, authenticated_client, user, create_user):
        org = create_organization(name="My Org", owner=user)
        member_user = create_user(email="member@example.com")
        membership = OrganizationMember.objects.create(
            organization=org, user=member_user, role=OrganizationMember.Role.MEMBER
        )
        
        url = reverse(
            "organizations:member-detail",
            kwargs={"org_pk": org.id, "member_pk": membership.id},
        )
        
        response = authenticated_client.patch(url, {"role": "admin"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == "admin"
        
        membership.refresh_from_db()
        assert membership.role == "admin"

    def test_remove_member(self, authenticated_client, user, create_user):
        org = create_organization(name="My Org", owner=user)
        member_user = create_user(email="member@example.com")
        membership = OrganizationMember.objects.create(
            organization=org, user=member_user, role=OrganizationMember.Role.MEMBER
        )
        
        url = reverse(
            "organizations:member-detail",
            kwargs={"org_pk": org.id, "member_pk": membership.id},
        )
        
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not OrganizationMember.objects.filter(id=membership.id).exists()
