# Sprint 1: Foundation & Design System

## Goal
Establish the architecture, tooling, and the Vanilla CSS design system every later sprint depends on.

## Key Components to Build
- **Folder structure (feature-sliced):** `src/app` (providers, router), `src/features/*`, `src/shared/{ui,hooks,lib,styles}`
- **Styles:** `tokens.css`, `reset.css`, `typography.css`, `animations.css`, `utilities.css`
- **Primitives (`shared/ui`):** Button (primary/ghost/danger/icon), Input, Textarea, Select, Checkbox, Badge, Avatar and AvatarStack, Card, Modal, Drawer, Dropdown/Popover, Tooltip, Skeleton, Spinner, EmptyState, Toast system
- **Utilities:** `cn()`, `useClickOutside`, `useDebounce`, `useHotkey`, FocusTrap and Portal
- **Tooling:** ESLint, Prettier, path aliases, env typing, Vitest and React Testing Library
- **Component gallery** at `/__ui` showing every primitive in every state

## API Integration
- `lib/axios.ts` instance with `baseURL` from env
- `QueryClientProvider` with sane defaults (`staleTime`, retry policy, error normalization)
- Shared TS types for pagination (`{count, next, previous, results}`) and DRF error shapes

## UI/UX Focus
- Tokens first. Everything references CSS variables:

```css
:root {
  --bg-0: #08080c; --bg-1: #0e0e14; --bg-2: #15151e;
  --surface-glass: rgba(255,255,255,0.04);
  --border-subtle: rgba(255,255,255,0.08);
  --accent-indigo: #6366f1; --accent-violet: #8b5cf6;
  --gradient-accent: linear-gradient(135deg, #6366f1, #8b5cf6);
  --glow-accent: 0 0 24px rgba(99,102,241,0.35);
  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --dur-fast: 120ms; --dur-base: 200ms;
}
```

- Glass recipe: translucent background, `backdrop-filter: blur(16px) saturate(140%)`, 1px subtle border, inner top highlight (`inset 0 1px 0 rgba(255,255,255,0.06)`).
- Inter variable font, self-hosted, `font-feature-settings: "cv11", "ss01"`, tabular numerals for counts.
- Primary buttons: gradient, soft glow on hover, 1px press-down on `:active`.
- Respect `prefers-reduced-motion` globally from day one.
- Define semantic colors for priorities (urgent, high, medium, low) and statuses now.

## Deliverable
A running app with the full design system visible at `/__ui`.
