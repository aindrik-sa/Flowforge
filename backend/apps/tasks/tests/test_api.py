"""
Tests for Task API endpoints.
"""
import pytest
from django.urls import reverse

from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn
from apps.tasks.models import Task, TaskLabel, TaskAssignment


@pytest.fixture
def setup_api(user, create_user, authenticated_client):
    """
    Full test setup: org, workspace, project, board, columns,
    org membership, project membership, and an authenticated client.
    """
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
    col_backlog = BoardColumn.objects.create(board=board, name="Backlog", slug="backlog", position=0)
    col_done = BoardColumn.objects.create(board=board, name="Done", slug="done", position=1)

    return {
        "org": org,
        "workspace": workspace,
        "project": project,
        "board": board,
        "col_backlog": col_backlog,
        "col_done": col_done,
        "client": authenticated_client,
        "user": user,
    }


@pytest.mark.django_db
class TestTaskListCreateAPI:
    def test_create_task(self, setup_api):
        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        response = setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Implement login",
            "priority": "high",
        }, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Implement login"
        assert data["task_number"] == 1
        assert data["identifier"] == "API-1"

    def test_list_tasks(self, setup_api):
        # Create two tasks via API
        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Task 1",
        }, format="json")
        setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Task 2",
        }, format="json")

        response = setup_api["client"].get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    def test_create_rejects_wrong_column(self, setup_api, user):
        """Column must belong to the project."""
        # Create a different project with its own column
        other_project = Project.objects.create(
            workspace=setup_api["workspace"],
            name="Other",
            key="OTH",
            created_by=user,
        )
        other_board = Board.objects.create(project=other_project, name="Board", is_default=True)
        other_col = BoardColumn.objects.create(board=other_board, name="Col", slug="col", position=0)

        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        response = setup_api["client"].post(url, {
            "column_id": str(other_col.id),
            "title": "Wrong column",
        }, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestTaskDetailAPI:
    def test_get_task(self, setup_api):
        # Create
        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        create_resp = setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Detail test",
        }, format="json")
        task_id = create_resp.json()["id"]

        # Retrieve
        response = setup_api["client"].get(f"/api/v1/tasks/{task_id}/")
        assert response.status_code == 200
        assert response.json()["title"] == "Detail test"

    def test_update_task(self, setup_api):
        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        create_resp = setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Original",
        }, format="json")
        task_id = create_resp.json()["id"]

        response = setup_api["client"].patch(
            f"/api/v1/tasks/{task_id}/",
            {"title": "Updated", "priority": "urgent"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
        assert response.json()["priority"] == "urgent"

    def test_delete_task(self, setup_api):
        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        create_resp = setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Delete me",
        }, format="json")
        task_id = create_resp.json()["id"]

        response = setup_api["client"].delete(f"/api/v1/tasks/{task_id}/")
        assert response.status_code == 204


@pytest.mark.django_db
class TestTaskMoveAPI:
    def test_move_task_to_column(self, setup_api):
        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        create_resp = setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Move me",
        }, format="json")
        task_id = create_resp.json()["id"]

        response = setup_api["client"].post(
            f"/api/v1/tasks/{task_id}/move/",
            {"column_id": str(setup_api["col_done"].id)},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["column"] == str(setup_api["col_done"].id)


@pytest.mark.django_db
class TestTaskAssignmentAPI:
    def test_assign_and_list(self, setup_api, create_user):
        # Create a task
        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        create_resp = setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Assign test",
        }, format="json")
        task_id = create_resp.json()["id"]

        assignee = create_user(email="dev@example.com")
        ProjectMember.objects.create(
            project=setup_api["project"],
            user=assignee,
            role=ProjectMember.Role.MEMBER,
        )

        # Assign
        response = setup_api["client"].post(
            f"/api/v1/tasks/{task_id}/assignees/",
            {"email": "dev@example.com"},
            format="json",
        )
        assert response.status_code == 201

        # List
        response = setup_api["client"].get(f"/api/v1/tasks/{task_id}/assignees/")
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestTaskLabelAPI:
    def test_create_label_and_attach(self, setup_api):
        project_id = setup_api["project"].id

        # Create label
        response = setup_api["client"].post(
            f"/api/v1/projects/{project_id}/labels/",
            {"name": "bug", "color": "#EF4444"},
            format="json",
        )
        assert response.status_code == 201
        label_id = response.json()["id"]

        # Create task
        task_resp = setup_api["client"].post(
            f"/api/v1/projects/{project_id}/tasks/",
            {
                "column_id": str(setup_api["col_backlog"].id),
                "title": "Buggy",
            },
            format="json",
        )
        task_id = task_resp.json()["id"]

        # Attach label
        response = setup_api["client"].post(
            f"/api/v1/tasks/{task_id}/labels/",
            {"label_id": label_id},
            format="json",
        )
        assert response.status_code == 200
        assert len(response.json()["labels"]) == 1


@pytest.mark.django_db
class TestTaskActivityAPI:
    def test_activity_log(self, setup_api):
        # Create task (generates 1 activity log)
        url = f"/api/v1/projects/{setup_api['project'].id}/tasks/"
        create_resp = setup_api["client"].post(url, {
            "column_id": str(setup_api["col_backlog"].id),
            "title": "Logged task",
        }, format="json")
        task_id = create_resp.json()["id"]

        # Update (generates more)
        setup_api["client"].patch(
            f"/api/v1/tasks/{task_id}/",
            {"priority": "urgent"},
            format="json",
        )

        response = setup_api["client"].get(f"/api/v1/tasks/{task_id}/activity/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # created + priority update
