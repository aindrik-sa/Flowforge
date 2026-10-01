"""
Tests for comment API endpoints.
"""
import pytest
from django.urls import reverse

from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn
from apps.tasks.models import Task
from apps.comments.models import Comment

@pytest.fixture
def setup_api(user, create_user, authenticated_client):
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
    col = BoardColumn.objects.create(board=board, name="Backlog", slug="backlog", position=0)
    task = Task.objects.create(
        project=project,
        column=col,
        title="Task 1",
        task_number=1,
        created_by=user,
    )

    return {
        "org": org,
        "workspace": workspace,
        "project": project,
        "board": board,
        "column": col,
        "task": task,
        "client": authenticated_client,
        "user": user,
    }

@pytest.mark.django_db
class TestCommentAPI:
    def test_create_and_list_comments(self, setup_api):
        task_id = setup_api["task"].id
        url = f"/api/v1/tasks/{task_id}/comments/"

        # Create
        response = setup_api["client"].post(url, {"body": "First post!"}, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["body"] == "First post!"
        assert data["task"] == str(task_id)

        # List
        list_resp = setup_api["client"].get(url)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

    def test_update_comment(self, setup_api):
        task_id = setup_api["task"].id
        url = f"/api/v1/tasks/{task_id}/comments/"
        
        # Create
        create_resp = setup_api["client"].post(url, {"body": "Original"}, format="json")
        comment_id = create_resp.json()["id"]
        
        # Update
        patch_url = f"/api/v1/comments/{comment_id}/"
        patch_resp = setup_api["client"].patch(patch_url, {"body": "Updated!"}, format="json")
        assert patch_resp.status_code == 200
        assert patch_resp.json()["body"] == "Updated!"
        assert patch_resp.json()["is_edited"] is True

    def test_delete_comment(self, setup_api):
        task_id = setup_api["task"].id
        url = f"/api/v1/tasks/{task_id}/comments/"
        
        create_resp = setup_api["client"].post(url, {"body": "To be deleted"}, format="json")
        comment_id = create_resp.json()["id"]
        
        delete_url = f"/api/v1/comments/{comment_id}/"
        del_resp = setup_api["client"].delete(delete_url)
        assert del_resp.status_code == 204
