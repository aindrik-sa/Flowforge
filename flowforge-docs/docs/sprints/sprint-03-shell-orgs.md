# Sprint 3: App Shell, Organizations & Workspaces

## Goal
The persistent application frame plus multi-tenant context switching.

## Key Components to Build
- **Layout:** AppShell (sidebar + topbar + content outlet), collapsible Sidebar, Topbar with breadcrumbs, UserMenu
- **Switchers:** OrgSwitcher, WorkspaceSwitcher (popover with search)
- **Pages:** OrgOnboarding (create first org), WorkspaceSettings, MembersPage (list, invite, change role)
- **Context:** `useCurrentOrg()` / `useCurrentWorkspace()` driven by URL params (`/:orgSlug/:workspaceSlug/...`) as the single source of truth
- **Query layer:** query key factory (e.g. `keys.workspaces.list(orgId)`)
- **Routing:** nested routes, lazy-loaded chunks with Suspense and skeleton fallbacks, 404 page, error boundary per route

## API Integration
- `GET/POST /organizations/`, `GET/PATCH /organizations/:id/`
- `GET/POST /workspaces/` (filtered by org), `GET/PATCH/DELETE /workspaces/:id/`
- `GET/POST /organizations/:id/members/`, invite and role-update endpoints

## UI/UX Focus
- Sidebar is a glass panel with a subtle vertical gradient. Active item: left accent bar, soft indigo glow, animated sliding indicator.
- Collapse animation animates width and fades labels. Tooltips on hover when collapsed.
- Switchers are Linear-style: compact trigger (avatar + name), popover with scale-and-fade entrance (`transform-origin` anchored to trigger).
- Avatars have deterministic gradient fallbacks from a name hash.
- Route transitions: gentle fade and 8px slide.

## Deliverable
Navigable shell with org and workspace switching reflected in the URL.
