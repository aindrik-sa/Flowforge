"""
Tests for attachment models and services.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.organizations.models import Organization
from apps.projects.models import Workspace, Project, Board, BoardColumn
from apps.tasks.models import Task, TaskActivityLog
from apps.attachments.models import Attachment
from apps.attachments.services import create_attachment, delete_attachment

@pytest.fixture
def setup_task(user):
    org = Organization.objects.create(name="Test Org", owner=user)
    workspace = Workspace.objects.create(organization=org, name="Engineering")
    project = Project.objects.create(
        workspace=workspace,
        name="Backend API",
        key="API",
        created_by=user,
    )
    board = Board.objects.create(project=project, name="Main Board", is_default=True)
    col = BoardColumn.objects.create(board=board, name="Backlog", slug="backlog", position=0)
    task = Task.objects.create(
        project=project,
        column=col,
        title="Test Task",
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
    }

@pytest.mark.django_db
class TestAttachmentServices:
    def test_create_attachment(self, user, setup_task):
        task = setup_task["task"]
        
        file = SimpleUploadedFile(
            "test.txt",
            b"Hello World",
            content_type="text/plain"
        )
        
        attachment = create_attachment(task=task, file=file, uploaded_by=user)
        
        assert attachment.original_filename == "test.txt"
        assert attachment.file_size == 11
        assert attachment.content_type == "text/plain"
        assert attachment.uploaded_by == user
        assert attachment.task == task
        assert not attachment.is_image
        assert attachment.file_extension == ".txt"
        
        # Check activity log
        logs = TaskActivityLog.objects.filter(task=task, field_name="attachment")
        assert logs.count() == 1

    def test_create_attachment_invalid_type(self, user, setup_task):
        task = setup_task["task"]
        
        file = SimpleUploadedFile(
            "test.exe",
            b"Binary content",
            content_type="application/x-msdownload"
        )
        
        with pytest.raises(ValueError, match="is not allowed"):
            create_attachment(task=task, file=file, uploaded_by=user)

    def test_delete_attachment(self, user, setup_task):
        task = setup_task["task"]
        
        file = SimpleUploadedFile(
            "test.png",
            b"Fake image data",
            content_type="image/png"
        )
        
        attachment = create_attachment(task=task, file=file, uploaded_by=user)
        assert Attachment.objects.count() == 1
        
        delete_attachment(attachment=attachment)
        assert Attachment.objects.count() == 0
