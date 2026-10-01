# Sprint 9: Reports & Dashboards

## Goal
Turn the reports API into beautiful, insightful data visualizations.

## Key Components to Build
- **Pages:** WorkspaceDashboard (home overview), ProjectReportsPage
- **StatCard:** value, delta vs previous period, sparkline
- **Charts** (Recharts is pragmatic, or hand-roll SVG for simple ones):
  - Tasks by status (donut)
  - Burndown/burnup (area/line)
  - Throughput/velocity (bar)
  - Tasks by priority (horizontal bars)
  - Workload per assignee (stacked bars)
  - Created vs completed over time
- **Controls:** DateRangePicker with presets (7d/30d/90d/custom), project filter, ExportButton (CSV if supported)
- **Extras:** MyTasksWidget, RecentActivityFeed, OverdueTasksList
- **Hooks:** `useReport(type, params)` with placeholder/previous data so range changes don't flash empty

## API Integration
- `GET /reports/summary/?workspace=&project=&from=&to=`
- `GET /reports/tasks-by-status/`, `/burndown/`, `/workload/`, `/velocity/` (match real endpoints)
- If Celery-backed reports return a "processing" state, poll with `refetchInterval` and show progress.

## UI/UX Focus
- Bento-grid of glass cards with varied spans, responsive from 1 to 4 columns.
- Indigo-to-violet gradient fills (`<linearGradient>`), soft glow strokes, very faint dashed gridlines.
- Custom glass tooltips with exact values and color swatches.
- Count-up animation for stat numbers on mount. Charts animate once, not on every refetch.
- Legend click toggles series. Legend hover dims other series.
- Chart-shaped skeletons. Errors are per card with Retry so one failure doesn't break the page.
- Accessible summaries for charts (visually hidden table or `aria-label` with key figures).

## Deliverable
Workspace dashboard and per-project reports with date range control.
