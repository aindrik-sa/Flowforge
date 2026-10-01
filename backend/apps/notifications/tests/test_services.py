"""
Tests for notification services.
"""
import pytest
from asgiref.testing import ApplicationCommunicator
from django.contrib.contenttypes.models import ContentType

from apps.organizations.models import Organization
from apps.projects.models import Workspace, Project, Board, BoardColumn
from apps.tasks.models import Task
from apps.notifications.models import Notification
from apps.notifications.services import create_notification, mark_as_read, mark_all_as_read
from config.asgi import application

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


@pytest.mark.django_db(transaction=True)
class TestNotificationServices:
    def test_create_notification(self, user, create_user, setup_task):
        actor = create_user(email="actor@example.com")
        task = setup_task["task"]
        
        notification = create_notification(
            recipient=user,
            actor=actor,
            verb="assigned you to",
            target=task
        )
        
        assert notification.recipient == user
        assert notification.actor == actor
        assert notification.verb == "assigned you to"
        assert notification.target == task
        assert not notification.is_read

    def test_mark_as_read(self, user, setup_task):
        notification = create_notification(
            recipient=user,
            verb="test",
        )
        
        updated = mark_as_read(notification=notification)
        assert updated.is_read

    def test_mark_all_as_read(self, user, setup_task):
        create_notification(recipient=user, verb="1")
        create_notification(recipient=user, verb="2")
        
        assert Notification.objects.filter(is_read=False).count() == 2
        
        mark_all_as_read(user=user)
        
        assert Notification.objects.filter(is_read=False).count() == 0
