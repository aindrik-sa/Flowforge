"""
Tests for attachment API endpoints.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn
from apps.tasks.models import Task

@pytest.fixture
def setup_api(user, authenticated_client):
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
        "task": task,
        "client": authenticated_client,
    }

@pytest.mark.django_db
class TestAttachmentAPI:
    def test_upload_and_list_attachments(self, setup_api):
        task_id = setup_api["task"].id
        url = f"/api/v1/tasks/{task_id}/attachments/"

        file = SimpleUploadedFile(
            "test_image.png",
            b"fake_image_data",
            content_type="image/png"
        )

        # Upload
        response = setup_api["client"].post(url, {"file": file}, format="multipart")
        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == "test_image.png"
        assert data["is_image"] is True
        assert data["file_url"] is not None

        # List
        list_resp = setup_api["client"].get(url)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

    def test_delete_attachment(self, setup_api):
        task_id = setup_api["task"].id
        url = f"/api/v1/tasks/{task_id}/attachments/"

        file = SimpleUploadedFile(
            "doc.pdf",
            b"fake_pdf_data",
            content_type="application/pdf"
        )

        upload_resp = setup_api["client"].post(url, {"file": file}, format="multipart")
        attachment_id = upload_resp.json()["id"]

        delete_url = f"/api/v1/attachments/{attachment_id}/"
        del_resp = setup_api["client"].delete(delete_url)
        assert del_resp.status_code == 204
