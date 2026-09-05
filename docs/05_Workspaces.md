# FlowForge — Workspaces

## Overview

Workspaces group `Project`s within an `Organization`. They help organize related projects together (e.g. "Engineering", "Marketing", "HR").

## Data Model

- `Workspace`: Represents a logical grouping. Has a `name`, `slug`, `description`, and belongs to an `Organization`.

## Access Control

- All `OrganizationMember`s can view workspaces within their organization.
- `OrganizationAdmin` and `OrganizationOwner` can create, update, or delete workspaces.
- Tenant Isolation is enforced by checking if the user belongs to the `workspace.organization`.

## API Endpoints

- `GET /api/v1/organizations/<org_id>/workspaces/` (List all workspaces in an org)
- `POST /api/v1/organizations/<org_id>/workspaces/` (Create a workspace)
- `GET /api/v1/workspaces/<id>/` (Retrieve workspace)
- `PATCH /api/v1/workspaces/<id>/` (Update workspace)
- `DELETE /api/v1/workspaces/<id>/` (Delete workspace)
