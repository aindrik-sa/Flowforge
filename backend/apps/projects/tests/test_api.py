"""
Tests for Project API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Workspace, Project, ProjectMember
from apps.organizations.services import create_organization
from apps.projects.services import create_workspace, create_project


@pytest.mark.django_db
class TestWorkspaceAPI:
    def test_list_workspaces(self, authenticated_client, user):
        org = create_organization(name="Test Org", owner=user)
        create_workspace(organization=org, name="Space 1")
        create_workspace(organization=org, name="Space 2")
        
        url = reverse("organizations:workspace-list-create", kwargs={"org_id": org.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_workspace(self, authenticated_client, user):
        org = create_organization(name="Test Org", owner=user)
        
        url = reverse("organizations:workspace-list-create", kwargs={"org_id": org.id})
        data = {"name": "New Space"}
        
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Space"


@pytest.mark.django_db
class TestProjectAPI:
    def test_list_projects(self, authenticated_client, user):
        org = create_organization(name="Test Org", owner=user)
        workspace = create_workspace(organization=org, name="Space")
        
        create_project(workspace=workspace, name="P1", key="P1", created_by=user)
        create_project(workspace=workspace, name="P2", key="P2", created_by=user)
        
        url = reverse("projects:project-list-create", kwargs={"workspace_id": workspace.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_create_project(self, authenticated_client, user):
        org = create_organization(name="Test Org", owner=user)
        workspace = create_workspace(organization=org, name="Space")
        
        url = reverse("projects:project-list-create", kwargs={"workspace_id": workspace.id})
        data = {"name": "New Project", "key": "NEW"}
        
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Project"
        assert response.data["key"] == "NEW"

    def test_project_filtering(self, authenticated_client, user):
        org = create_organization(name="Test Org", owner=user)
        workspace = create_workspace(organization=org, name="Space")
        
        create_project(
            workspace=workspace, name="P1", key="P1", created_by=user, status=Project.Status.ACTIVE
        )
        create_project(
            workspace=workspace, name="P2", key="P2", created_by=user, status=Project.Status.PLANNED
        )
        
        url = reverse("projects:project-list-create", kwargs={"workspace_id": workspace.id})
        response = authenticated_client.get(url, {"status": "active"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "P1"

    def test_project_search(self, authenticated_client, user):
        org = create_organization(name="Test Org", owner=user)
        workspace = create_workspace(organization=org, name="Space")
        
        create_project(
            workspace=workspace, name="Backend API", key="BE", created_by=user
        )
        create_project(
            workspace=workspace, name="Frontend Web", key="FE", created_by=user
        )
        
        url = reverse("projects:project-list-create", kwargs={"workspace_id": workspace.id})
        response = authenticated_client.get(url, {"search": "Backend"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Backend API"
