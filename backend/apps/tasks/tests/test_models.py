"""
Tests for Task models and constraints.
"""
import pytest
from django.db import IntegrityError

from apps.organizations.models import Organization
from apps.projects.models import Workspace, Project, Board, BoardColumn
from apps.tasks.models import Task, TaskLabel, TaskAssignment, TaskActivityLog


@pytest.fixture
def setup_project(user):
    """Create a full project hierarchy for task tests."""
    org = Organization.objects.create(name="Test Org", owner=user)
    workspace = Workspace.objects.create(organization=org, name="Engineering")
    project = Project.objects.create(
        workspace=workspace,
        name="Backend API",
        key="API",
        created_by=user,
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
    }


@pytest.mark.django_db
class TestTaskModel:
    def test_task_creation(self, user, setup_project):
        task = Task.objects.create(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Implement login",
            task_number=1,
            created_by=user,
        )

        assert task.title == "Implement login"
        assert task.task_number == 1
        assert task.priority == Task.Priority.MEDIUM
        assert task.identifier == "API-1"

    def test_unique_task_number_per_project(self, user, setup_project):
        Task.objects.create(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 1",
            task_number=1,
            created_by=user,
        )

        with pytest.raises(IntegrityError):
            Task.objects.create(
                project=setup_project["project"],
                column=setup_project["col_backlog"],
                title="Task 2",
                task_number=1,
                created_by=user,
            )

    def test_task_identifier_property(self, user, setup_project):
        task = Task.objects.create(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Feature X",
            task_number=42,
            created_by=user,
        )
        assert task.identifier == "API-42"


@pytest.mark.django_db
class TestTaskLabelModel:
    def test_label_creation(self, user, setup_project):
        label = TaskLabel.objects.create(
            project=setup_project["project"],
            name="bug",
            color="#EF4444",
        )
        assert label.name == "bug"
        assert label.color == "#EF4444"

    def test_unique_label_name_per_project(self, user, setup_project):
        TaskLabel.objects.create(
            project=setup_project["project"],
            name="bug",
        )
        with pytest.raises(IntegrityError):
            TaskLabel.objects.create(
                project=setup_project["project"],
                name="bug",
            )


@pytest.mark.django_db
class TestTaskAssignmentModel:
    def test_assignment_creation(self, user, create_user, setup_project):
        task = Task.objects.create(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task",
            task_number=1,
            created_by=user,
        )
        assignee = create_user(email="assignee@example.com")
        assignment = TaskAssignment.objects.create(task=task, user=assignee)

        assert assignment.task == task
        assert assignment.user == assignee

    def test_unique_assignment(self, user, create_user, setup_project):
        task = Task.objects.create(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task",
            task_number=1,
            created_by=user,
        )
        assignee = create_user(email="assignee@example.com")
        TaskAssignment.objects.create(task=task, user=assignee)

        with pytest.raises(IntegrityError):
            TaskAssignment.objects.create(task=task, user=assignee)
