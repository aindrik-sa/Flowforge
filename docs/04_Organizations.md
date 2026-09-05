# FlowForge — Organizations

## Overview

Organizations act as the primary tenant boundary in FlowForge. Every workspace, project, and task belongs to an organization. 

A user can belong to multiple organizations and have different roles in each.

## Data Model

- `Organization`: Represents the company or team.
- `OrganizationMember`: Links a `User` to an `Organization` and stores their `role`.

## Roles

1. **Owner**: Full access, can delete the organization. Cannot be removed or demoted directly.
2. **Admin**: Can manage organization settings and members.
3. **Manager**: Can manage workspaces and projects (to be implemented).
4. **Member**: Standard access, can view and interact with projects.
5. **Viewer**: Read-only access.

## Tenant Isolation

Tenant isolation is enforced at multiple layers:
1. **Selectors**: `get_user_organizations()` is the only way to list organizations.
2. **Permissions**: `IsOrganizationMember`, `IsOrganizationAdmin`, `IsOrganizationOwner` enforce access control on object retrieval.

## API Endpoints

- `GET /api/v1/organizations/` (List organizations for current user)
- `POST /api/v1/organizations/` (Create organization)
- `GET /api/v1/organizations/<id>/` (Retrieve organization)
- `PATCH /api/v1/organizations/<id>/` (Update organization)
- `DELETE /api/v1/organizations/<id>/` (Delete organization)
- `GET /api/v1/organizations/<id>/members/` (List members)
- `POST /api/v1/organizations/<id>/members/` (Add member)
- `PATCH /api/v1/organizations/<org_id>/members/<member_id>/` (Change member role)
- `DELETE /api/v1/organizations/<org_id>/members/<member_id>/` (Remove member)
