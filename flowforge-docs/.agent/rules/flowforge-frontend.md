# FlowForge Frontend Rules

- Stack: Vite, React, TypeScript, React Router v6, Axios, TanStack Query, @hello-pangea/dnd.
- NO UI component libraries (MUI, Bootstrap, Tailwind, Chakra). Vanilla CSS only.
- All colors, spacing, radii, shadows and motion values come from CSS variables in `src/shared/styles/tokens.css`. Never hardcode them.
- Aesthetic: premium dark mode, glassmorphism, indigo/violet gradients, Inter font, Linear-like density and speed.
- Server state lives in TanStack Query. URL state lives in the router (filters, open task, tabs). Local UI state stays in components. No global store unless justified.
- Every screen needs loading (skeleton), empty, and error states, and must be keyboard accessible.
- Respect `prefers-reduced-motion`. Animate only `transform` and `opacity`. UI feedback animations must be 300ms or shorter.
- Priority and status are never conveyed by color alone (use icon + color).
- The API contract is `docs/openapi.yaml` if present. It is the source of truth over any endpoint path written in the sprint docs.
- Follow `docs/FRONTEND_PLAN.md`. Work ONLY on the sprint the user specifies. Do not start the next sprint.
- Before writing code, present an implementation plan. After finishing, summarize what was built and list deviations from the spec.
