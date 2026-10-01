# Sprint 4: Projects

## Goal
Browse, create, and configure projects within a workspace.

## Key Components to Build
- **Pages:** ProjectsPage (grid/list toggle), ProjectLayout (tabs: Board, List, Reports, Settings), ProjectSettingsPage
- **Components:** ProjectCard, CreateProjectModal (name, key, description, icon, color), ProjectMemberManager, ArchiveProjectDialog
- **Hooks:** `useProjects`, `useProject`, `useCreateProject` (optimistic insert), `useUpdateProject`
- **Shared:** debounced search and filter bar, reusable ConfirmDialog

## API Integration
- `GET /projects/?workspace=:id&search=&ordering=`
- `POST /projects/`, `GET/PATCH/DELETE /projects/:id/`
- Project members endpoints
- Pagination via `useInfiniteQuery` or page controls

## UI/UX Focus
- ProjectCard: gradient icon tile, progress ring (completed vs total), avatar stack, hover lift (`translateY(-2px)`), cursor-following spotlight border glow via `--mouse-x/--mouse-y` and a radial gradient.
- Staggered entrance animation by index (capped).
- Skeleton cards match final layout exactly (no layout shift).
- Friendly empty state with inline SVG illustration and gradient CTA.
- Create modal opens with spring-like scale, autofocuses name. `Cmd/Ctrl+Enter` submits.

## Deliverable
Create, search, edit, and archive projects; project tab layout in place.
