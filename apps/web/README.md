# Thiên Hạc — Astrology Frontend

Web client for Thiên Hạc built around the "Luminous Twilight" astrology design.

Read [`AGENTS.md`](./AGENTS.md) before changing anything — it holds the token rules,
breakpoint system, runtime theming contract, and backend contract for this project.

## Getting started

```bash
cp .env.example .env.local
pnpm install
pnpm dev
```

The backend runs separately, from the repo root:

```bash
uv run uvicorn tuvi_api.main:app --reload
```

## Login

The FastAPI backend owns login; this app only renders it. `src/lib/auth-client.ts`
calls `/api/v1/auth/*`, and the API keeps the session in an httpOnly cookie.
Next forwards every `/api/*` request to `API_ORIGIN`, so the cookie belongs to
this site. See the [API guide](../api/README.md#authentication) for the routes.

- **Email and password.** Accounts must confirm their email before they can
  sign in. Sign-up sends a confirmation link; signing in with an unconfirmed
  email sends a fresh one. The link signs the user in and returns to `/login`,
  which routes on as usual.
- **Password reset.** `/forgot-password` emails a link that opens
  `/reset-password`. Saving a new password signs out every session of the
  account. Both links expire after one hour.
- **Google.** Enabled when the API has `AUTH__GOOGLE_CLIENT_ID` and
  `AUTH__GOOGLE_CLIENT_SECRET`. In Google Cloud Console, create an OAuth client
  of type **Web application** and add
  `http://localhost:3000/api/v1/auth/google/callback` (in production,
  `https://your-domain.com/api/v1/auth/google/callback`) to **Authorized
  redirect URIs**. After sign-in, users with saved charts go to `/ho-so`; users
  without them go to `/`. A failed sign-in returns to `/login?error=google`.
- **Email.** The API sends mail through [Resend](https://resend.com) with
  `AUTH__RESEND_API_KEY` and `AUTH__EMAIL_FROM` (a domain verified in Resend).
  Without them, the API logs each email, link included, instead of sending it.

This app requests only `openid`, `email`, and `profile` from Google. Google
allows users outside **Test users** to sign in even while the app is in
**Testing** mode. See [Google's audience rules](https://support.google.com/cloud/answer/15549945?hl=en).
Never commit the downloaded credentials JSON.

## Commands

| Command | What it does |
| --- | --- |
| `pnpm dev` | Dev server (Turbopack) |
| `pnpm build` | Production build |
| `pnpm start` | Serve the build |
| `pnpm lint` | ESLint |
| `pnpm typecheck` | `tsc --noEmit` |
| `pnpm format` | Prettier write |
| `pnpm test` | Vitest |

## Design source of truth

`docs/design/tu-vi-app-responsible.html` is a complete working prototype of all eight
screens. When a question about visual behaviour comes up, read its CSS rather than
guessing.
