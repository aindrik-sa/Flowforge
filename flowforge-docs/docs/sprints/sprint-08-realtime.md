# Sprint 8: Real-Time Layer (WebSockets)

## Goal
Live notifications, live comments, and live board updates through a robust WebSocket client.

## Key Components to Build
- **Infrastructure:**
  - `WebSocketClient` class: JWT auth (query param or subprotocol, per your Channels auth middleware), exponential backoff with jitter, heartbeat/ping, re-auth on token refresh
  - `RealtimeProvider` exposing connection state
  - `useRealtimeEvent(type, handler)` hook
  - Typed event map (`notification.created`, `comment.created`, `task.updated`, `task.moved`, ...)
- **Notifications:** NotificationBell (unread badge), NotificationPanel (tabs All/Unread, grouped by day), NotificationItem (deep-links to the task), "Mark all read", full NotificationsPage
- **Cache sync:** handlers use `setQueryData` or targeted `invalidateQueries`, not blanket refetches
- **Presence (optional):** "who's viewing" avatars, typing indicators
- **Utilities:** ConnectionStatus indicator, resync on tab refocus, optional browser Notification API opt-in

## API Integration
- `ws(s)://.../ws/notifications/` (plus per-project/per-task channels if routed)
- `GET /notifications/?is_read=`, `PATCH /notifications/:id/read/`, `POST /notifications/mark-all-read/`
- Fallback: poll `GET /notifications/unread-count/` while the socket is down

## UI/UX Focus
- Bell badge pops with a spring scale and glow. One-time ring animation, reduced-motion aware.
- Glass toast for high-priority events with a deep-link action.
- Remote changes: card moved by someone else animates to its new spot (FLIP-style) with a brief violet flash and a small avatar tag.
- Never overwrite a field the user is editing. Queue the update and show "Updated by Sam, click to refresh".
- Connection dot in the sidebar footer: green, amber pulsing while reconnecting, red when offline, with tooltip.

## Tests
Unit tests for backoff logic, reconnect, and event-to-cache handlers.

## Deliverable
Two browser sessions see each other's comments, moves, and notifications live.
