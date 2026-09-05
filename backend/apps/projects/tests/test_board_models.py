import pytest
from django.db import IntegrityError

from apps.projects.models import Board, BoardColumn
from apps.projects.services import (
    create_board,
    create_board_column,
    reorder_columns,
    delete_board_column,
)

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


class TestBoardModel:
    def test_board_creation(self, project):
        board = Board.objects.create(project=project, name="Sprint 1")
        assert board.project == project
        assert board.name == "Sprint 1"
        assert board.slug == "sprint-1"
        assert board.is_default is False

    def test_unique_board_slug_per_project(self, project):
        Board.objects.create(project=project, name="Sprint", slug="sprint")
        with pytest.raises(IntegrityError):
            Board.objects.create(project=project, name="Sprint 2", slug="sprint")


class TestBoardServices:
    def test_create_board_with_default_columns(self, project):
        board = create_board(project=project, name="Main Board")
        assert board.name == "Main Board"
        assert board.columns.count() == 5
        
        column_names = list(board.columns.values_list("name", flat=True))
        assert column_names == ["Backlog", "To Do", "In Progress", "Review", "Done"]

    def test_create_board_column(self, project):
        board = create_board(project=project, name="Main Board")
        # Add column at the end
        new_col = create_board_column(board=board, name="Archived")
        assert new_col.position == 5
        
        # Add column at position 2
        shifted_col = create_board_column(board=board, name="On Hold", position=2)
        assert shifted_col.position == 2
        assert board.columns.get(name="In Progress").position == 3

    def test_reorder_columns(self, project):
        board = create_board(project=project, name="Main Board")
        columns = list(board.columns.all())
        
        # Move "Backlog" (pos 0) to pos 4 (end)
        new_order = [columns[1].id, columns[2].id, columns[3].id, columns[4].id, columns[0].id]
        reorder_columns(board=board, ordered_column_ids=new_order)
        
        reordered = list(board.columns.all().order_by("position"))
        assert reordered[0].name == "To Do"
        assert reordered[4].name == "Backlog"

    def test_delete_board_column_shifts_positions(self, project):
        board = create_board(project=project, name="Main Board")
        col_to_delete = board.columns.get(name="In Progress")
        
        delete_board_column(column=col_to_delete)
        
        assert board.columns.count() == 4
        assert board.columns.get(name="Review").position == 2
        assert board.columns.get(name="Done").position == 3
