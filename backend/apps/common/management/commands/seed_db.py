import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.organizations.models import Organization, OrganizationMember
from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn
from apps.tasks.models import Task, TaskAssignment
from apps.tasks.services import create_task

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with test data for development."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Create superuser
        admin, created = User.objects.get_or_create(email="admin@flowforge.internal", defaults={"is_superuser": True, "is_staff": True})
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin user (admin@flowforge.internal / admin123)"))

        # Create basic user
        user, created = User.objects.get_or_create(email="user@flowforge.internal", defaults={"first_name": "Test", "last_name": "User"})
        if created:
            user.set_password("user123")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created standard user (user@flowforge.internal / user123)"))

        # Organization
        org, _ = Organization.objects.get_or_create(name="Acme Corp", owner=admin)
        OrganizationMember.objects.get_or_create(organization=org, user=admin, role=OrganizationMember.Role.OWNER)
        OrganizationMember.objects.get_or_create(organization=org, user=user, role=OrganizationMember.Role.MEMBER)

        # Workspace
        workspace, _ = Workspace.objects.get_or_create(organization=org, name="Engineering")

        # Project
        project, _ = Project.objects.get_or_create(
            workspace=workspace,
            key="ENG",
            defaults={"name": "Core Platform", "created_by": admin}
        )
        ProjectMember.objects.get_or_create(project=project, user=admin, role=ProjectMember.Role.MANAGER)
        ProjectMember.objects.get_or_create(project=project, user=user, role=ProjectMember.Role.MEMBER)

        # Board and Columns
        board, _ = Board.objects.get_or_create(project=project, name="Sprint 1", defaults={"is_default": True})
        
        col_todo, _ = BoardColumn.objects.get_or_create(board=board, name="To Do", defaults={"position": 0})
        col_in_progress, _ = BoardColumn.objects.get_or_create(board=board, name="In Progress", defaults={"position": 1})
        col_done, _ = BoardColumn.objects.get_or_create(board=board, name="Done", defaults={"position": 2})

        # Tasks
        if not Task.objects.filter(project=project).exists():
            for i in range(1, 11):
                col = random.choice([col_todo, col_in_progress, col_done])
                task = create_task(
                    project=project,
                    column=col,
                    title=f"Sample Task {i}",
                    created_by=admin,
                    description="This is a seeded task.",
                    priority=random.choice(Task.Priority.choices)[0]
                )
                if random.choice([True, False]):
                    TaskAssignment.objects.get_or_create(task=task, user=user)

            self.stdout.write(self.style.SUCCESS("Created 10 sample tasks."))

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
