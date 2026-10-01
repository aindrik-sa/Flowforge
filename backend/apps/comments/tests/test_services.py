"""
Tests for comment models and services.
"""
import pytest

from apps.organizations.models import Organization
from apps.projects.models import Workspace, Project, Board, BoardColumn
from apps.tasks.models import Task, TaskActivityLog
from apps.comments.models import Comment
from apps.comments.services import create_comment, update_comment, delete_comment

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
class TestCommentServices:
    def test_create_comment(self, user, setup_task):
        task = setup_task["task"]
        comment = create_comment(task=task, author=user, body="Hello World")
        assert comment.body == "Hello World"
        assert comment.author == user
        assert comment.task == task
        assert not comment.is_edited
        
        # Check activity log
        logs = TaskActivityLog.objects.filter(task=task, field_name="comment")
        assert logs.count() == 1
        assert logs.first().action == TaskActivityLog.Action.UPDATED

    def test_create_comment_with_mentions(self, user, create_user, setup_task):
        other_user = create_user(email="dev@example.com")
        task = setup_task["task"]
        
        comment = create_comment(task=task, author=user, body="Hey @dev@example.com!")
        assert other_user in comment.mentions.all()

    def test_update_comment(self, user, setup_task):
        task = setup_task["task"]
        comment = create_comment(task=task, author=user, body="Original")
        
        updated = update_comment(comment=comment, body="Updated", updated_by=user)
        assert updated.body == "Updated"
        assert updated.is_edited

    def test_create_reply(self, user, setup_task):
        task = setup_task["task"]
        parent = create_comment(task=task, author=user, body="Parent")
        reply = create_comment(task=task, author=user, body="Reply", parent=parent)
        
        assert reply.parent == parent
        assert reply in parent.replies.all()

    def test_delete_comment_cascades(self, user, setup_task):
        task = setup_task["task"]
        parent = create_comment(task=task, author=user, body="Parent")
        create_comment(task=task, author=user, body="Reply", parent=parent)
        
        delete_comment(comment=parent)
        
        assert Comment.objects.count() == 0
