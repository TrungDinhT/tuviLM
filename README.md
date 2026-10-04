# TuviLM

See the [API guide](api/README.md) and [frontend guide](astrology_styled_frontend/README.md)
for application setup.

## Bootstrap an administrator

Administrator access is granted by a private server-side script, not a public
signup option or API. The script promotes an existing Better Auth account; it
does not create password hashes or change the account's plan, balance or email
verification status.

1. Register an account at `/register` using an email you control and a strong,
   unique password. Confirm that the account belongs to you; email verification
   is not currently enforced by the app.
2. On a trusted machine with private MongoDB access, run the script from the
   repository root. First check that `.env` values `AUTH__MONGO_URI` and
   `AUTH__DATABASE_NAME` point to the same database as the frontend's
   `MONGODB_URI` and `MONGODB_DATABASE`.

   ```bash
   uv sync
   uv run python -m api.auth.bootstrap_admin --email admin@example.com
   ```

3. The script finds the account by email; you do not need to look up a user ID.
   Check the printed database, email and user ID, then type the full email to
   confirm. The script revokes existing sessions **before** granting the admin
   role. A missing account, duplicate email or cancelled confirmation does not
   change data. Email matching ignores leading/trailing spaces and letter case.
4. Sign in again and open `/admin/redeem-codes`, or use the admin link in your
   profile. Choose the coin amount, code type and lifetime to create a code.

The script never asks for or prints a password; use the password you registered.
An already-admin account is left unchanged. The script works on standalone
MongoDB as well as replica sets, without adding a dependency. Session revocation
and role promotion are separate writes: run it before using the new account,
without concurrent sign-ins. If a database write fails, inspect the account role
before retrying; sessions may already have been revoked.

Keep MongoDB private and authenticated in production. Never expose this script
through an HTTP route, run it during startup, or store database credentials in Git.

Coin redemption itself requires a MongoDB replica set; see the
[redemption requirements](api/README.md#coin-redemption-codes).
