# Sprint 7: Task Detail, Comments & Attachments

## Goal
A rich task detail experience where all collaboration happens.

## Key Components to Build
- **Container:** TaskDetailDrawer (right slide-over, route-driven via `?task=FF-142` or `/tasks/:id` so links are shareable) plus a full-page variant
- **Inline editors:** EditableTitle, RichDescription (start with textarea/markdown; avoid heavy editors), StatusSelect, PrioritySelect, AssigneePicker (searchable multi-select), DatePicker (custom, Vanilla CSS), LabelPicker
- **Comments:** CommentList, CommentItem (edit, delete, timestamps), CommentComposer with `@mention` autocomplete, relative time ("2m ago") with absolute-time tooltip
- **Attachments:** AttachmentDropzone (drag and paste), AttachmentList, upload progress via Axios `onUploadProgress`, image lightbox, file-type icons, size/type validation
- **Activity:** ActivityTimeline if the backend exposes it
- **Hooks:** `useTask`, `useUpdateTask` (per-field autosave, debounce, optimistic), `useComments`, `useAddComment`, `useUploadAttachment`

## API Integration
- `GET/PATCH/DELETE /tasks/:id/`
- `GET/POST /tasks/:id/comments/`, `PATCH/DELETE /comments/:id/`
- `GET/POST /tasks/:id/attachments/` (`multipart/form-data`), `DELETE /attachments/:id/`
- Activity/history endpoint if available

## UI/UX Focus
- Drawer slides from the right with backdrop blur on the board. `Esc` closes. `J`/`K` move to next/previous task.
- Linear-style click-to-edit with no separate edit mode. Saved state shows a tiny check that fades out.
- Properties sidebar: two-column label/value grid with hover-highlighted rows.
- Comments slide up subtly. Composer grows with content and shows a gradient send button once non-empty.
- Dropzone has a dashed gradient border that animates on drag-over. Uploads show a slim gradient progress bar.
- Optimistic comments appear instantly at reduced opacity ("sending") and resolve, or show Retry on failure.

## Deliverable
Open any task from the board, edit every field inline, comment, and attach files.
