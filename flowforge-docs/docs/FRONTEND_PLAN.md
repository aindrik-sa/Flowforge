# FlowForge Frontend: 10-Sprint Implementation Plan

**Product:** FlowForge, an enterprise project management tool (Jira/Linear class).
**Backend (complete):** Django, DRF, PostgreSQL, Celery, Redis, Django Channels. Modular monolith. JWT auth, Organizations and Workspaces, Projects and Kanban Boards, Tasks, Comments, Attachments, Reports, real-time Notifications.
**Frontend stack:** Vite, React, TypeScript, Axios, TanStack Query, React Router v6, `@hello-pangea/dnd`, native WebSockets, Vanilla CSS design system.

> Endpoint paths in the sprint files follow DRF conventions and are assumptions. Reconcile them with the real API (`docs/openapi.yaml`).

## Sprint Index

| # | Sprint | File |
|---|--------|------|
| 1 | Foundation & Design System | `sprints/sprint-01-foundation.md` |
| 2 | Authentication & Session | `sprints/sprint-02-auth.md` |
| 3 | App Shell, Orgs & Workspaces | `sprints/sprint-03-shell-orgs.md` |
| 4 | Projects | `sprints/sprint-04-projects.md` |
| 5 | Kanban Board (Read-Only) & Task Creation | `sprints/sprint-05-board.md` |
| 6 | Drag & Drop, Optimistic Updates | `sprints/sprint-06-dnd.md` |
| 7 | Task Detail, Comments & Attachments | `sprints/sprint-07-task-detail.md` |
| 8 | Real-Time Layer (WebSockets) | `sprints/sprint-08-realtime.md` |
| 9 | Reports & Dashboards | `sprints/sprint-09-reports.md` |
| 10 | Polish, Performance, A11y, Release | `sprints/sprint-10-polish.md` |

## Dependencies
- Sprint 6 depends on 5. Sprint 7 depends on 5. Sprint 8 depends on 7 (benefits from 6).
- Sprint 9 is largely independent after Sprint 4 and can run in parallel.

## Definition of Done (Every Sprint)
- Typed (no `any` without justification), responsive, keyboard-accessible.
- Loading, empty, and error states exist.
- Design tokens only. No hardcoded colors.
- Lint, typecheck, and tests pass.

## State Rules
- Server state: TanStack Query. URL state: router. Local UI state: components.
- Use a query key factory for predictable invalidation.

## Risk Areas (Spike Early)
1. Token refresh race conditions (Sprint 2)
2. Position/ordering semantics matching the backend (Sprint 6)
3. WebSocket auth handshake (Sprint 8)
