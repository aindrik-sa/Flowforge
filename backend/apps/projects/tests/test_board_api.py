import pytest
from django.urls import reverse
from rest_framework import status

from apps.projects.models import Board
from apps.projects.services import create_board

pytestmark = pytest.mark.django_db

from apps.organizations.services import create_organization
from apps.projects.services import create_workspace, create_project

@pytest.fixture
def project(user):
    org = create_organization(name="Test Org", owner=user)
    workspace = create_workspace(organization=org, name="Test Workspace")
    return create_project(
        workspace=workspace,
        name="Test Project",
        key="TEST",
        created_by=user,
    )


class TestBoardAPI:
    def test_list_boards(self, authenticated_client, project):
        url = reverse("projects:board-list-create", kwargs={"pk": project.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # A project gets a default board automatically created during project creation
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Main Board"
        
        # Add a second board explicitly
        create_board(project=project, name="Second Board")
        response = authenticated_client.get(url)
        assert len(response.data) == 2

    def test_create_board(self, authenticated_client, project):
        url = reverse("projects:board-list-create", kwargs={"pk": project.id})
        payload = {"name": "Test Board"}
        response = authenticated_client.post(url, data=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Board"
        assert response.data["slug"] == "test-board"
        
        # Default columns should be created
        assert len(response.data["columns"]) == 5

    def test_retrieve_board(self, authenticated_client, project):
        board = Board.objects.filter(project=project).first()
        url = reverse("projects:board-detail", kwargs={"pk": board.id})
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == board.name
        assert len(response.data["columns"]) == 5

    def test_update_board(self, authenticated_client, project):
        board = Board.objects.filter(project=project).first()
        url = reverse("projects:board-detail", kwargs={"pk": board.id})
        
        payload = {"name": "Updated Name"}
        response = authenticated_client.patch(url, data=payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"
        
        board.refresh_from_db()
        assert board.name == "Updated Name"

    def test_delete_board(self, authenticated_client, project):
        # A project must have at least one board. So we create a second to delete it.
        board2 = create_board(project=project, name="Board 2")
        url = reverse("projects:board-detail", kwargs={"pk": board2.id})
        
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Board.objects.filter(id=board2.id).exists()

    def test_cannot_delete_only_board(self, authenticated_client, project):
        board = Board.objects.filter(project=project).first()
        url = reverse("projects:board-detail", kwargs={"pk": board.id})
        
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Board.objects.filter(id=board.id).exists()


class TestBoardColumnAPI:
    def test_list_columns(self, authenticated_client, project):
        board = Board.objects.filter(project=project).first()
        url = reverse("projects:column-list-create", kwargs={"pk": board.id})
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_create_column(self, authenticated_client, project):
        board = Board.objects.filter(project=project).first()
        url = reverse("projects:column-list-create", kwargs={"pk": board.id})
        
        payload = {"name": "Testing"}
        response = authenticated_client.post(url, data=payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Testing"
        assert response.data["position"] == 5

    def test_reorder_columns(self, authenticated_client, project):
        board = Board.objects.filter(project=project).first()
        url = reverse("projects:column-reorder", kwargs={"pk": board.id})
        
        columns = list(board.columns.all())
        # Move first to last
        new_order = [str(c.id) for c in columns[1:]] + [str(columns[0].id)]
        
        payload = {"ordered_column_ids": new_order}
        response = authenticated_client.post(url, data=payload)
        assert response.status_code == status.HTTP_200_OK
        
        assert response.data[0]["name"] == columns[1].name
        assert response.data[4]["name"] == columns[0].name
