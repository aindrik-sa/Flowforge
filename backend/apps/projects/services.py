from django.db import models, transaction
from django.utils.text import slugify

from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn
from apps.organizations.models import Organization

# Default Kanban columns created with every new board.
DEFAULT_COLUMNS = [
    {"name": "Backlog", "color": "#9E9E9E", "position": 0},
    {"name": "To Do", "color": "#2196F3", "position": 1},
    {"name": "In Progress", "color": "#FF9800", "position": 2},
    {"name": "Review", "color": "#9C27B0", "position": 3},
    {"name": "Done", "color": "#4CAF50", "position": 4},
]


def create_workspace(
    *,
    organization: Organization,
    name: str,
    description: str = "",
    slug: str = "",
) -> Workspace:
    """Create a new workspace within an organization."""
    if not slug:
        slug = slugify(name)
        
    base_slug = slug
    counter = 1
    while Workspace.objects.filter(organization=organization, slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    workspace = Workspace.objects.create(
        organization=organization,
        name=name,
        slug=slug,
        description=description,
    )
    return workspace


def create_project(
    *,
    workspace: Workspace,
    name: str,
    key: str,
    created_by,
    description: str = "",
    slug: str = "",
    status: str = Project.Status.PLANNED,
    start_date=None,
    due_date=None,
) -> Project:
    """
    Create a new project, assign the creator as a manager,
    and auto-create a default Kanban board with standard columns.
    """
    if not slug:
        slug = slugify(name)
        
    base_slug = slug
    counter = 1
    while Project.objects.filter(workspace=workspace, slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    with transaction.atomic():
        project = Project.objects.create(
            workspace=workspace,
            name=name,
            key=key,
            slug=slug,
            description=description,
            status=status,
            start_date=start_date,
            due_date=due_date,
            created_by=created_by,
        )

        ProjectMember.objects.create(
            project=project,
            user=created_by,
            role=ProjectMember.Role.MANAGER,
        )

        # Auto-create a default board
        create_board(project=project, name="Main Board", is_default=True)

    return project


def add_project_member(
    *,
    project: Project,
    user,
    role: str = ProjectMember.Role.MEMBER,
) -> ProjectMember:
    """Add a user to a project with a specific role."""
    member = ProjectMember.objects.create(
        project=project,
        user=user,
        role=role,
    )
    return member


def remove_project_member(
    *,
    project: Project,
    user,
) -> None:
    """Remove a user from a project."""
    membership = ProjectMember.objects.filter(
        project=project,
        user=user,
    )
    deleted_count, _ = membership.delete()

    if deleted_count == 0:
        raise ValueError("User is not a member of this project.")


def change_project_member_role(
    *,
    project: Project,
    user,
    new_role: str,
) -> ProjectMember:
    """Change a project member's role."""
    try:
        membership = ProjectMember.objects.get(
            project=project,
            user=user,
        )
    except ProjectMember.DoesNotExist:
        raise ValueError("User is not a member of this project.")

    membership.role = new_role
    membership.save(update_fields=["role", "updated_at"])
    return membership


# ---------------------------------------------------------------------------
# Board Services
# ---------------------------------------------------------------------------


def create_board(
    *,
    project: Project,
    name: str,
    description: str = "",
    slug: str = "",
    is_default: bool = False,
) -> Board:
    """
    Create a new board with default Kanban columns.

    WHAT: Atomic operation — creates board + 5 default columns.
    WHY:  An empty board with no columns is useless. Users expect a
          ready-to-use Kanban board out of the box.
    IMPORTANT: If is_default=True, any other default board in the same
               project is demoted first.
    """
    if not slug:
        slug = slugify(name)

    base_slug = slug
    counter = 1
    while Board.objects.filter(project=project, slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    with transaction.atomic():
        # Demote existing default board if this one is being set as default
        if is_default:
            Board.objects.filter(project=project, is_default=True).update(
                is_default=False
            )

        board = Board.objects.create(
            project=project,
            name=name,
            slug=slug,
            description=description,
            is_default=is_default,
        )

        # Create default columns
        columns = [
            BoardColumn(
                board=board,
                name=col["name"],
                slug=slugify(col["name"]),
                position=col["position"],
                color=col["color"],
            )
            for col in DEFAULT_COLUMNS
        ]
        BoardColumn.objects.bulk_create(columns)

    return board


def create_board_column(
    *,
    board: Board,
    name: str,
    position: int = None,
    color: str = "",
    wip_limit: int = None,
    slug: str = "",
) -> BoardColumn:
    """
    Add a new column to a board.

    If position is None, appends at the end. If a position is specified,
    shifts existing columns at that position and beyond to make room.
    """
    if not slug:
        slug = slugify(name)

    base_slug = slug
    counter = 1
    while BoardColumn.objects.filter(board=board, slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    with transaction.atomic():
        if position is None:
            # Append at the end
            max_pos = BoardColumn.objects.filter(board=board).count()
            position = max_pos
        else:
            # Shift columns at this position and beyond.
            # Must iterate in reverse to avoid unique constraint violations
            columns_to_shift = list(
                BoardColumn.objects.filter(
                    board=board, position__gte=position
                ).order_by("-position")
            )
            for col in columns_to_shift:
                col.position += 1
                col.save(update_fields=["position"])

        column = BoardColumn.objects.create(
            board=board,
            name=name,
            slug=slug,
            position=position,
            color=color,
            wip_limit=wip_limit,
        )

    return column


def reorder_columns(
    *,
    board: Board,
    ordered_column_ids: list,
) -> None:
    """
    Reorder columns by setting their positions based on the order
    of IDs provided.

    WHAT: Accepts a list of column UUIDs in the desired display order.
    WHY:  Drag-and-drop reordering on the frontend sends the new order;
          we update positions atomically to avoid constraint violations.
    IMPORTANT: All column IDs for the board must be included.
    """
    existing_ids = set(
        BoardColumn.objects.filter(board=board).values_list("id", flat=True)
    )
    provided_ids = set(ordered_column_ids)

    if existing_ids != provided_ids:
        raise ValueError(
            "The provided column IDs do not match the board's columns. "
            "All columns must be included, with no extras."
        )

    with transaction.atomic():
        # Temporarily set positions to a huge offset to avoid
        # unique constraint violations and PositiveIntegerField limits
        for idx, col_id in enumerate(ordered_column_ids):
            BoardColumn.objects.filter(id=col_id).update(position=100000 + idx)

        # Now set the real positions
        for idx, col_id in enumerate(ordered_column_ids):
            BoardColumn.objects.filter(id=col_id).update(position=idx)


def delete_board_column(*, column: BoardColumn) -> None:
    """
    Delete a column and re-normalize the positions of remaining columns.

    WHAT: Removes the column and closes the gap in the position sequence.
    WHY:  If column at position 2 is deleted, columns at positions 3, 4, 5
          should become 2, 3, 4 — no gaps.
    """
    board = column.board
    deleted_position = column.position

    with transaction.atomic():
        column.delete()

        # Shift down columns that were after the deleted one
        # Must iterate in forward order to avoid unique constraint violations
        columns_to_shift = list(
            BoardColumn.objects.filter(
                board=board, position__gt=deleted_position
            ).order_by("position")
        )
        for col in columns_to_shift:
            col.position -= 1
            col.save(update_fields=["position"])

