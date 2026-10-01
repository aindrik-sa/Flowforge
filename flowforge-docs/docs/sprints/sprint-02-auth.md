# Sprint 2: Authentication & Session Management

## Goal
Secure, seamless JWT auth with silent refresh and route protection.

## Key Components to Build
- **Pages:** LoginPage, RegisterPage, ForgotPasswordPage (if backend supports it)
- **Auth layer:** AuthProvider, `useAuth()`, ProtectedRoute, PublicOnlyRoute
- **Token handling:** `tokenStorage` module. Access token in memory, refresh token in `localStorage` (or httpOnly cookie if the backend supports it, which is preferable)
- **Axios interceptors:** request attaches Bearer token. Response on 401 queues concurrent requests, refreshes once, replays them.
- **Forms:** lightweight `useForm` hook (or React Hook Form + Zod) with inline field errors mapped from DRF's error shape

## API Integration
- `POST /auth/register/`
- `POST /auth/login/` (or `/token/`)
- `POST /auth/token/refresh/`
- `POST /auth/logout/` (blacklist refresh token)
- `GET /users/me/` (hydrate user on app boot)

## UI/UX Focus
- Split-screen layout. Left: animated mesh-gradient background (slow indigo/violet blobs via `@keyframes`) with tagline. Right: glass card with the form.
- Floating-label inputs with an animated gradient focus ring (`mask` or `background-clip`).
- Submit button: inline spinner, then brief success checkmark morph before redirect.
- Form-level errors shake once (4px horizontal keyframe). Never use alerts.
- Branded splash with logo pulse while `/users/me/` resolves, so there is no flash of the login page.

## Risks
Token refresh race conditions. Write unit tests for the interceptor queue.

## Deliverable
Register, log in, refresh silently, log out, and protected routes working end to end.
