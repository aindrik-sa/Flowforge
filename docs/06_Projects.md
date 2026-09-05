# FlowForge — Projects

## Overview

Projects contain boards, tasks, and members. Every `Project` belongs to a `Workspace`.

## Data Model

- `Project`: Represents a project. Has a `name`, `key` (e.g., FLOW), `slug`, `description`, `status`, `start_date`, `due_date`, and a `created_by` relationship.
- `ProjectMember`: Links a `User` to a `Project` with a specific role.

## Statuses
- Planned
- Active
- On Hold
- Completed
- Archived

## Roles
- `Manager`: Can manage the project settings and members.
- `Member`: Standard access, can manage tasks.
- `Viewer`: Read-only access to the project.

## Access Control

- `Project` creation: Any `OrganizationMember` can create a project inside any workspace they have access to. The creator automatically becomes a `ProjectMember` with the `Manager` role.
- Reading projects: `ProjectMember`s can view the project details. Also, any `OrganizationAdmin` or `OrganizationOwner` has implicit read access.
- Updating/Deleting projects: Only users with the `Manager` role can update or delete the project.
- Tenant Isolation: `get_projects()` is scoped to the specific `Workspace`, which is scoped to the `Organization`.

## API Endpoints

- `GET /api/v1/workspaces/<workspace_id>/projects/` (List all projects, supports search, filtering, and pagination)
- `POST /api/v1/workspaces/<workspace_id>/projects/` (Create a project)
- `GET /api/v1/projects/<id>/` (Retrieve project)
- `PATCH /api/v1/projects/<id>/` (Update project)
- `DELETE /api/v1/projects/<id>/` (Delete project)
- `GET /api/v1/projects/<id>/members/` (List members)
- `POST /api/v1/projects/<id>/members/` (Add member)
- `PATCH /api/v1/projects/<project_id>/members/<member_id>/` (Change member role)
- `DELETE /api/v1/projects/<project_id>/members/<member_id>/` (Remove member)
