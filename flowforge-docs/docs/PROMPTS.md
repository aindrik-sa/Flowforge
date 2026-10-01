# Antigravity Prompts

Use Planning mode. Run one prompt per sprint, review the plan before approving, and commit after each sprint.

## Setup (once)
```
Read .agent/rules/flowforge-frontend.md and docs/FRONTEND_PLAN.md.
If docs/openapi.yaml exists, read it and treat it as the API source of truth.
Confirm you understand the constraints. Do not write code yet.
```

## Per-sprint template
Replace NN and NAME with the sprint number and file name.
```
Read docs/FRONTEND_PLAN.md and docs/sprints/sprint-NN-NAME.md.
Implement Sprint NN only. Before writing code, give me an implementation plan
and the list of files you will create or change. Do not start the next sprint.
When done: run lint, typecheck, and tests, summarize what was built, and list
any deviations from the spec or assumptions you made about the API.
```

## Sprint-specific add-ons

- **Sprint 2:** "Also write unit tests for the 401 refresh queue, including concurrent requests and refresh failure."
- **Sprint 6:** "Before the UI, build and test the ordering utility in isolation. Ask me what position format the backend expects if openapi.yaml doesn't make it clear."
- **Sprint 8:** "Start with a standalone WebSocketClient with tests for backoff and reconnect before wiring it into the UI."
- **Any UI sprint:** "Use the browser agent to open the dev server, screenshot each new screen in loading, empty, and populated states, and compare against the UI/UX Focus section."

## Parallel option
Sprints 6 and 9 touch different folders (`features/board` vs `features/reports`) and can run as separate agents after Sprint 5 and Sprint 4 respectively.
