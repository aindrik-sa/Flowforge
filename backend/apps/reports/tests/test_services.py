import pytest
from django.core.cache import cache

from apps.organizations.models import Organization
from apps.projects.models import Workspace, Project, Board, BoardColumn
from apps.tasks.models import Task, TaskAssignment
from apps.reports.services import get_project_dashboard_stats, get_user_productivity_stats

@pytest.fixture
def setup_reports(user):
    # Ensure cache is clear before tests
    cache.clear()
    
    org = Organization.objects.create(name="Test Org", owner=user)
    workspace = Workspace.objects.create(organization=org, name="Engineering")
    project = Project.objects.create(
        workspace=workspace,
        name="Backend API",
        key="API",
        created_by=user,
    )
    board = Board.objects.create(project=project, name="Main Board", is_default=True)
    
    # Statuses
    todo_col = BoardColumn.objects.create(board=board, name="To Do", slug="to-do", position=0)
    done_col = BoardColumn.objects.create(board=board, name="Done", slug="done", position=1)

    t1 = Task.objects.create(
        project=project,
        column=todo_col,
        title="Task 1",
        task_number=1,
        created_by=user,
    )
    t2 = Task.objects.create(
        project=project,
        column=done_col,
        title="Task 2",
        task_number=2,
        created_by=user,
    )
    
    # Assign user to both
    TaskAssignment.objects.create(task=t1, user=user)
    TaskAssignment.objects.create(task=t2, user=user)

    return {
        "project": project,
        "user": user,
    }


@pytest.mark.django_db
class TestReportServices:
    def test_get_project_dashboard_stats(self, setup_reports):
        project = setup_reports["project"]
        stats = get_project_dashboard_stats(str(project.id))
        
        assert stats["total_tasks"] == 2
        assert stats["completed_tasks"] == 1
        assert stats["pending_tasks"] == 1
        assert stats["completion_percentage"] == 50
        
        # Test caching
        cached_stats = cache.get(f"project_stats_{project.id}")
        assert cached_stats is not None
        assert cached_stats["total_tasks"] == 2

    def test_get_user_productivity_stats(self, setup_reports):
        user = setup_reports["user"]
        stats = get_user_productivity_stats(str(user.id))
        
        assert stats["completed_last_30_days"] == 1
        assert stats["current_pending_tasks"] == 1

        cached_stats = cache.get(f"user_productivity_{user.id}")
        assert cached_stats is not None
        
    def test_invalid_project(self):
        with pytest.raises(ValueError):
            import uuid
            get_project_dashboard_stats(str(uuid.uuid4()))
