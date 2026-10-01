import pytest
from django.core.cache import cache

from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn
from apps.tasks.models import Task, TaskAssignment

@pytest.fixture
def setup_api(user, create_user, authenticated_client):
    cache.clear()
    
    org = Organization.objects.create(name="Test Org", owner=user)
    OrganizationMember.objects.create(
        organization=org,
        user=user,
        role=OrganizationMember.Role.OWNER,
    )
    workspace = Workspace.objects.create(organization=org, name="Engineering")
    project = Project.objects.create(
        workspace=workspace,
        name="Backend API",
        key="API",
        created_by=user,
    )
    ProjectMember.objects.create(
        project=project,
        user=user,
        role=ProjectMember.Role.MANAGER,
    )
    board = Board.objects.create(project=project, name="Main Board", is_default=True)
    done_col = BoardColumn.objects.create(board=board, name="Done", slug="done", position=0)
    
    task = Task.objects.create(
        project=project,
        column=done_col,
        title="Task 1",
        task_number=1,
        created_by=user,
    )
    TaskAssignment.objects.create(task=task, user=user)
    
    other_user = create_user(email="other@example.com")

    return {
        "project": project,
        "user": user,
        "other_user": other_user,
        "client": authenticated_client,
    }


@pytest.mark.django_db
class TestReportsAPI:
    def test_project_dashboard(self, setup_api):
        project = setup_api["project"]
        url = f"/api/v1/projects/{project.id}/dashboard/"
        
        response = setup_api["client"].get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 1
        assert data["completed_tasks"] == 1
        assert data["completion_percentage"] == 100

    def test_user_productivity(self, setup_api):
        user = setup_api["user"]
        url = f"/api/v1/users/{user.id}/productivity/"
        
        response = setup_api["client"].get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["completed_last_30_days"] == 1

    def test_user_productivity_forbidden(self, setup_api):
        other = setup_api["other_user"]
        url = f"/api/v1/users/{other.id}/productivity/"
        
        response = setup_api["client"].get(url)
        assert response.status_code == 403
