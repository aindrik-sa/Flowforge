"""
Tests for Task service functions.
"""
import pytest

from apps.organizations.models import Organization
from apps.projects.models import Workspace, Project, Board, BoardColumn
from apps.tasks.models import Task, TaskLabel, TaskAssignment, TaskActivityLog
from apps.tasks.services import (
    create_task,
    update_task,
    move_task,
    reorder_tasks,
    assign_task,
    unassign_task,
    create_label,
    add_label_to_task,
    remove_label_from_task,
)


@pytest.fixture
def setup_project(user):
    """Create a full project hierarchy for task service tests."""
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
    col_progress = BoardColumn.objects.create(board=board, name="In Progress", slug="in-progress", position=1)
    col_done = BoardColumn.objects.create(board=board, name="Done", slug="done", position=2)
    return {
        "org": org,
        "workspace": workspace,
        "project": project,
        "board": board,
        "col_backlog": col_backlog,
        "col_progress": col_progress,
        "col_done": col_done,
    }


@pytest.mark.django_db
class TestCreateTask:
    def test_creates_task_with_auto_number(self, user, setup_project):
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="First task",
            created_by=user,
        )
        assert task.task_number == 1
        assert task.identifier == "API-1"
        assert task.position == 0

    def test_auto_increments_task_number(self, user, setup_project):
        create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 1",
            created_by=user,
        )
        task2 = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 2",
            created_by=user,
        )
        assert task2.task_number == 2

    def test_logs_created_activity(self, user, setup_project):
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Logged task",
            created_by=user,
        )
        logs = TaskActivityLog.objects.filter(task=task)
        assert logs.count() == 1
        assert logs.first().action == TaskActivityLog.Action.CREATED

    def test_positions_within_column(self, user, setup_project):
        t1 = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 1",
            created_by=user,
        )
        t2 = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 2",
            created_by=user,
        )
        assert t1.position == 0
        assert t2.position == 1


@pytest.mark.django_db
class TestUpdateTask:
    def test_updates_fields_and_logs(self, user, setup_project):
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Original",
            created_by=user,
        )
        updated = update_task(
            task=task,
            updated_by=user,
            title="Updated Title",
            priority=Task.Priority.HIGH,
        )
        assert updated.title == "Updated Title"
        assert updated.priority == Task.Priority.HIGH

        # 1 created + 2 updates (title, priority)
        logs = TaskActivityLog.objects.filter(task=task)
        assert logs.count() == 3

    def test_no_log_when_unchanged(self, user, setup_project):
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Same",
            created_by=user,
        )
        update_task(task=task, updated_by=user, title="Same")

        # Only the "created" log
        logs = TaskActivityLog.objects.filter(task=task)
        assert logs.count() == 1


@pytest.mark.django_db
class TestMoveTask:
    def test_move_to_different_column(self, user, setup_project):
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Movable task",
            created_by=user,
        )
        moved = move_task(
            task=task,
            target_column=setup_project["col_progress"],
            moved_by=user,
        )
        assert moved.column == setup_project["col_progress"]

        logs = TaskActivityLog.objects.filter(
            task=task, action=TaskActivityLog.Action.MOVED
        )
        assert logs.count() == 1

    def test_move_normalizes_old_column(self, user, setup_project):
        t1 = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 1",
            created_by=user,
        )
        t2 = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 2",
            created_by=user,
        )
        # Move t1 out
        move_task(
            task=t1,
            target_column=setup_project["col_progress"],
            moved_by=user,
        )
        t2.refresh_from_db()
        assert t2.position == 0  # Gap closed


@pytest.mark.django_db
class TestReorderTasks:
    def test_reorder_within_column(self, user, setup_project):
        t1 = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 1",
            created_by=user,
        )
        t2 = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 2",
            created_by=user,
        )
        t3 = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task 3",
            created_by=user,
        )

        # Reverse order
        reorder_tasks(
            column=setup_project["col_backlog"],
            ordered_task_ids=[t3.id, t2.id, t1.id],
        )

        t1.refresh_from_db()
        t2.refresh_from_db()
        t3.refresh_from_db()
        assert t3.position == 0
        assert t2.position == 1
        assert t1.position == 2

    def test_reorder_fails_with_wrong_ids(self, user, setup_project):
        import uuid
        create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task",
            created_by=user,
        )
        with pytest.raises(ValueError, match="do not match"):
            reorder_tasks(
                column=setup_project["col_backlog"],
                ordered_task_ids=[uuid.uuid4()],
            )


@pytest.mark.django_db
class TestAssignment:
    def test_assign_and_unassign(self, user, create_user, setup_project):
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Assignable",
            created_by=user,
        )
        assignee = create_user(email="dev@example.com")

        assignment = assign_task(task=task, user=assignee, assigned_by=user)
        assert assignment.user == assignee
        assert TaskAssignment.objects.filter(task=task).count() == 1

        unassign_task(task=task, user=assignee, removed_by=user)
        assert TaskAssignment.objects.filter(task=task).count() == 0

    def test_unassign_nonexistent_raises(self, user, create_user, setup_project):
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Task",
            created_by=user,
        )
        other = create_user(email="nobody@example.com")

        with pytest.raises(ValueError, match="not assigned"):
            unassign_task(task=task, user=other, removed_by=user)


@pytest.mark.django_db
class TestLabels:
    def test_create_and_attach_label(self, user, setup_project):
        label = create_label(
            project=setup_project["project"],
            name="bug",
            color="#EF4444",
        )
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Buggy task",
            created_by=user,
        )

        add_label_to_task(task=task, label=label, added_by=user)
        assert label in task.labels.all()

        logs = TaskActivityLog.objects.filter(
            task=task, action=TaskActivityLog.Action.LABEL_ADDED
        )
        assert logs.count() == 1

    def test_remove_label(self, user, setup_project):
        label = create_label(
            project=setup_project["project"],
            name="feature",
        )
        task = create_task(
            project=setup_project["project"],
            column=setup_project["col_backlog"],
            title="Feature task",
            created_by=user,
        )
        add_label_to_task(task=task, label=label, added_by=user)
        remove_label_from_task(task=task, label=label, removed_by=user)

        assert label not in task.labels.all()
