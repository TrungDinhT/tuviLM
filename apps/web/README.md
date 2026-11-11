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

## Google sign-in (OAuth 2.0)

Google sign-in is already handled by Better Auth. It is enabled when both
`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are configured; email/password
sign-in remains available.

1. In Google Cloud Console, create an OAuth client with type **Web application**,
   not **Desktop app**.
2. Add `http://localhost:3000/api/auth/callback/google` to **Authorized redirect URIs**.
3. Set the client credentials in this directory's ignored `.env.local` file:

   ```dotenv
   GOOGLE_CLIENT_ID=your-web-client-id
   GOOGLE_CLIENT_SECRET=your-web-client-secret
   ```

Keep `BETTER_AUTH_URL=http://localhost:3000` for local development. Restart
`pnpm dev` after configuring credentials, then open `/login` and choose Google.
After sign-in, users with saved charts go to `/ho-so`; users without them go to `/`.

For production, set `BETTER_AUTH_URL` to the public HTTPS origin and register
`https://your-domain.com/api/auth/callback/google` on the Google OAuth client.
The callback must match exactly.

This app requests only `openid`, `email`, and `profile`. Google allows users
outside **Test users** to sign in even while the app is in **Testing** mode.
That list is not an application access allowlist for basic Google sign-in.
See [Google's audience rules](https://support.google.com/cloud/answer/15549945?hl=en).

Never commit the downloaded credentials JSON or `.env.local`, and never prefix
the Google credentials with `NEXT_PUBLIC_`.

See the [Better Auth Google guide](https://better-auth.com/docs/authentication/google).

## Email verification and password reset

Email/password accounts must confirm their email before they can sign in.
Sign-up sends a confirmation link; signing in with an unconfirmed email sends a
fresh one. The link signs the user in and returns to `/login`, which routes on
as usual. Google accounts arrive already verified.

`/forgot-password` emails a reset link that opens `/reset-password`. Saving a new
password signs out every existing session of that account. Both links expire
after one hour.

Mail is sent through the [Resend](https://resend.com) HTTP API. Set both values
in `.env.local`:

```dotenv
RESEND_API_KEY=re_...
EMAIL_FROM="Thiên Hạc <no-reply@your-domain.com>"
```

The `EMAIL_FROM` domain must be verified in Resend. Without these values,
`pnpm dev` prints each email, link included, to its console instead of sending
it; a production server logs an error and sends nothing.

Accounts that were already signed in before verification became mandatory keep
their session until it ends; they must verify at their next sign-in.

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
