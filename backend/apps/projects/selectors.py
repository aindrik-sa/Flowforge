from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn
from apps.organizations.models import Organization


def get_workspaces(*, organization: Organization):
    """Return all workspaces in an organization."""
    return Workspace.objects.filter(organization=organization)


def get_projects(*, workspace: Workspace):
    """Return all projects in a workspace."""
    return Project.objects.filter(workspace=workspace)


def get_user_projects(*, organization: Organization, user):
    """
    Return all projects in an organization that the user is a member of.
    """
    return Project.objects.filter(
        workspace__organization=organization,
        members__user=user,
    ).distinct()


def get_project_members(*, project: Project):
    """Return all members of a project."""
    return ProjectMember.objects.filter(project=project).select_related("user")


def get_boards(*, project: Project):
    """Return all boards for a project, with columns prefetched."""
    return Board.objects.filter(project=project).prefetch_related("columns")


def get_board_columns(*, board: Board):
    """Return all columns for a board, ordered by position."""
    return BoardColumn.objects.filter(board=board).order_by("position")

