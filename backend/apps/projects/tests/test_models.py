"""
Tests for Project and Workspace models.
"""
import pytest
from django.db import IntegrityError

from apps.organizations.models import Organization
from apps.projects.models import Workspace, Project, ProjectMember


@pytest.mark.django_db
class TestWorkspaceModel:
    def test_workspace_creation(self, user):
        org = Organization.objects.create(name="Test Org", owner=user)
        workspace = Workspace.objects.create(organization=org, name="Engineering")
        
        assert workspace.name == "Engineering"
        assert workspace.slug == "engineering"
        assert workspace.organization == org

    def test_unique_workspace_name(self, user):
        org = Organization.objects.create(name="Test Org", owner=user)
        Workspace.objects.create(organization=org, name="Engineering")
        
        with pytest.raises(IntegrityError):
            Workspace.objects.create(organization=org, name="Engineering")


@pytest.mark.django_db
class TestProjectModel:
    def test_project_creation(self, user):
        org = Organization.objects.create(name="Test Org", owner=user)
        workspace = Workspace.objects.create(organization=org, name="Engineering")
        
        project = Project.objects.create(
            workspace=workspace,
            name="Backend API",
            key="API",
            created_by=user,
        )
        
        assert project.name == "Backend API"
        assert project.slug == "backend-api"
        assert project.key == "API"
        assert project.status == Project.Status.PLANNED


@pytest.mark.django_db
class TestProjectMemberModel:
    def test_project_member_creation(self, user, create_user):
        org = Organization.objects.create(name="Test Org", owner=user)
        workspace = Workspace.objects.create(organization=org, name="Engineering")
        project = Project.objects.create(
            workspace=workspace,
            name="Backend API",
            key="API",
            created_by=user,
        )
        
        member_user = create_user(email="member@example.com")
        member = ProjectMember.objects.create(
            project=project,
            user=member_user,
            role=ProjectMember.Role.MEMBER,
        )
        
        assert member.project == project
        assert member.user == member_user
        assert member.role == ProjectMember.Role.MEMBER

    def test_unique_project_member(self, user, create_user):
        org = Organization.objects.create(name="Test Org", owner=user)
        workspace = Workspace.objects.create(organization=org, name="Engineering")
        project = Project.objects.create(
            workspace=workspace,
            name="Backend API",
            key="API",
            created_by=user,
        )
        
        member_user = create_user(email="member@example.com")
        ProjectMember.objects.create(
            project=project,
            user=member_user,
            role=ProjectMember.Role.MEMBER,
        )
        
        with pytest.raises(IntegrityError):
            ProjectMember.objects.create(
                project=project,
                user=member_user,
                role=ProjectMember.Role.MANAGER,
            )
