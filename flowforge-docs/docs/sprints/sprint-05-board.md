# Sprint 5: Kanban Board (Read-Only) & Task Creation

## Goal
Render the full board from API data with task cards, plus basic task CRUD, before adding drag-and-drop.

## Key Components to Build
- **Board:** BoardPage, BoardColumn, ColumnHeader (title, count, WIP indicator, menu), TaskCard, AddColumnButton
- **Task bits:** PriorityIcon, AssigneeAvatar, LabelChip, DueDateBadge (overdue state), TaskKey (e.g. `FF-142`)
- **Creation:** QuickAddTask (inline at column bottom), CreateTaskModal (full form)
- **Toolbar:** BoardToolbar with filters (assignee, priority, label, due date), search, "group by" placeholder
- **Hooks:** `useBoard(projectId)`, `useTasks`, `useCreateTask`, `useColumns`, `useCreateColumn`, `useRenameColumn`, `useDeleteColumn`
- **Data:** group tasks by column in a `select` function. Wrap TaskCard in `React.memo`.

## API Integration
- `GET /projects/:id/columns/` (ordered)
- `GET /tasks/?project=:id&assignee=&priority=&search=`
- `POST /tasks/`, `PATCH /tasks/:id/`
- `POST/PATCH/DELETE /columns/:id/`
- `GET /users/?project=:id` for assignee pickers

## UI/UX Focus
- Columns are translucent glass lanes with a tinted status dot in the header. Independent scrolling, thin custom scrollbars, fade masks at top and bottom edges.
- Task cards are compact and dense (Linear-like): title, key, priority icon, assignee, due date. Hover raises border brightness and reveals quick actions.
- Priority uses icon AND color, never color alone.
- Quick-add expands inline with smooth height transition. `Enter` creates and keeps focus for rapid entry.
- New tasks animate in (scale from 0.96 with a brief fading indigo highlight).
- Board skeleton shows ghost columns with ghost cards.

## Deliverable
Fully rendered board with filters, column CRUD, and task creation.
