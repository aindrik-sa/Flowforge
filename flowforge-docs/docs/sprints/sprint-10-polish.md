# Sprint 10: Polish, Performance, Accessibility & Release Readiness

## Goal
Elevate the product from "works" to "feels like Linear" and make it production-ready.

## Key Components to Build
- **Command palette (`Cmd/Ctrl+K`):** global search across tasks, projects, actions. Fuzzy matching, recents, keyboard-only navigation.
- **Shortcuts:** `C` create task, `G` then `B` go to board, `?` opens cheat sheet. Central registry so shortcuts are discoverable.
- **Settings:** ProfileSettings (avatar upload, name, password), AppearanceSettings (accent presets, density, reduced-motion toggle), notification preferences
- **Robustness:** global ErrorBoundary with recovery UI, offline banner, standardized empty/error states, 403/404 handling, session-expired flow
- **Performance:** route-level code-splitting audit, bundle analysis, virtualized lists (`@tanstack/react-virtual`) for large columns and notifications, lazy images, prefetch on hover (`prefetchQuery`), React Profiler memoization audit
- **Quality:** unit tests (ordering logic, token refresh, WS reconnect), component tests for critical flows, Playwright E2E: login, create project, create task, drag, comment
- **Accessibility:** focus management in modals/drawers, ARIA roles and labels, visible focus rings, WCAG AA contrast audit, screen-reader pass on the board
- **Release:** env configs, CI (lint, typecheck, test, build), Sentry or equivalent, Lighthouse budget

## API Integration
- `GET /search/` (or compose from list endpoints with `search` params)
- `PATCH /users/me/`, password change, avatar upload
- Notification preference endpoints if available

## UI/UX Focus
- **Motion audit:** consistent easing and durations from tokens, nothing over 300ms for UI feedback, no layout-property animation.
- **Perceived speed:** optimistic updates everywhere, hover prefetch, matching skeletons, no spinner over 200ms where a skeleton fits.
- **Micro-details:** custom selection color, thin scrollbars, subtle noise overlay, gradient glow focus rings, hover/press states on every interactive element.
- **Responsive pass:** sidebar becomes a drawer on tablet/mobile, scroll-snapping Kanban on small screens, bottom sheet instead of drawer for task detail.
- **Consistency sweep:** spacing scale, icon sizes and stroke widths, copy tone in empty/error states.
- **Final QA checklist:** every screen has loading, empty, error, and success states.

## Deliverable
Production-ready build with CI, tests, and accessibility sign-off.
