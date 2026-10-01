# Sprint 6: Drag & Drop, Optimistic Updates

## Goal
Fluid, reliable drag-and-drop for tasks and columns, with instant feedback and safe rollback.

## Key Components to Build
- **DnD setup:** `DragDropContext` at board level, `Droppable` per column, `Draggable` per card, droppable board container for column reordering (`type="COLUMN"`)
- **Hooks:** `useMoveTask`, `useReorderColumns` with `onMutate` (snapshot + optimistic update), `onError` (rollback + toast), `onSettled` (invalidate)
- **Ordering util:** compute new position. Prefer fractional indexing or float `position` (midpoint of neighbors) so one row updates per move. CONFIRM what the backend expects before implementing.
- **Accessibility and robustness:** auto-scroll for long columns and wide boards, keyboard drag (Space + arrows), live-region announcements
- **Edge cases:** drop into empty column, cancel with `Esc`, simultaneous moves, WIP limit warning

## API Integration
- `PATCH /tasks/:id/move/` (or `PATCH /tasks/:id/` with `{column, position}`)
- `PATCH /columns/:id/` or `POST /projects/:id/columns/reorder/`
- On `409`/`400` conflicts: refetch and show a non-blocking toast

## UI/UX Focus
- Dragged card: ~2 degree rotation, elevated shadow, indigo glow border, scale 1.03.
- Drop target: soft gradient highlight and animated placeholder gap (transition on placeholder height).
- Valid columns brighten, others dim slightly.
- `transform`/`opacity` only, so animation stays on the compositor.
- On drop, card settles with a quick spring and subtle pulse.
- Never block the UI on the network call. Moves must feel instant on slow connections.

## Tests
Unit tests for the ordering utility (start, end, middle, empty column, collisions/rebalance).

## Deliverable
Drag tasks between and within columns, reorder columns, with rollback on failure.
