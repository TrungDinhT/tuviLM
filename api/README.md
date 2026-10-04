# TuviLM API

FastAPI backend for TuviLM UI.

## Current status
- Real route: `POST /api/v1/laso/build`
- Real route: `POST /api/v1/laso/cau-phu`
- Real route: `POST /api/v1/laso/build_sao_luu`
- Conversation history routes are mounted from `api/chat/routes.py`:
  - `POST /api/v1/anonymous`
  - `POST /api/v1/chart-profiles`
  - `GET /api/v1/chart-profiles`
  - `PATCH /api/v1/chart-profiles/{chart_profile_id}`
  - `POST /api/v1/chart-profiles/{chart_profile_id}/sessions`
  - `GET /api/v1/chart-profiles/{chart_profile_id}/sessions`
  - `GET /api/v1/sessions/{session_id}`
  - `POST /api/v1/sessions/{session_id}/chat/stream`

## Install dependencies
From repo root:

```bash
uv sync
```

or if you use pip directly:

```bash
pip install fastapi uvicorn pydantic
```

## Run server
From repo root:

```bash
uv run uvicorn api.main:app --reload --port 8000
```

## Health check

```bash
curl http://localhost:8000/api/v1/health
```

## Authentication

Better Auth runs in `astrology_styled_frontend`. Configure the backend's `.env`
using `.env.example`; `AUTH__BASE_URL`, `AUTH__MONGO_URI` and
`AUTH__DATABASE_NAME` must match the frontend's `BETTER_AUTH_URL`, `MONGODB_URI`
and `MONGODB_DATABASE`.

Saved chart profiles, sessions and chat require a signed-in account. The web
client retrieves a JWT from `/api/auth/token` and sends it as
`Authorization: Bearer <token>`. The backend verifies its signature, issuer,
audience and expiration using `/api/auth/jwks`, then checks the associated
Better Auth session and reads the user's current role from MongoDB.

`GET /api/v1/me` returns the authenticated `user_id`, `role`, `plan` and `balance`.
Missing, invalid or revoked credentials return `401`; an authenticated user lacking
an administrator role receives `403` from `require_admin`. Authentication
service outages return `503` rather than granting access.

To bootstrap an administrator, register a normal account and run the private
`api.auth.bootstrap_admin` script. Follow the [administrator setup guide](../README.md#bootstrap-an-administrator)
for configuration, confirmation and session revocation. No public endpoint grants
administrator roles.

Health, chart preview and chart casting remain public. The legacy anonymous
ID endpoint remains available, but `X-Anonymous-Owner-Id` no longer grants
access to saved profiles or chat. Existing anonymous data is not reassigned
to accounts automatically.

The web client resets chart and chat state when the active account changes.
Its persisted chart is restored only for the matching account. Requests from
the previous account are cancelled; private requests also check that their
fresh token belongs to the account that started them.

Saved chart names can be changed with
`PATCH /api/v1/chart-profiles/{chart_profile_id}` and
`{"display_name": "My chart"}`. The name is trimmed and must contain 1–80
characters. Only the profile owner may rename it; missing, deleted or another
account's profiles return `404`. Renaming leaves birth data and chat history
unchanged, and re-casting the same birth data preserves the edited name.

Automatically saved charts are named `Lá số 1`, `Lá số 2`, and so on, rather
than using birth or save dates. Names are allocated and stored by the server,
not derived from the list order. Existing automatic birth-date names are
converted once during storage initialization; custom names are retained.
Names are stripped before storage, including existing padded names.
Within an account, duplicate names receive a suffix such as `Family (2)`.
Matching ignores letter case and extra whitespace, but preserves Vietnamese
accents. A unique database index also prevents concurrent requests from
creating duplicate names. Deleted profiles keep their names reserved so
restoring the same chart does not change its name.

## Account plans and balance

Role and plan are separate: `role` is `user` or `admin`; `plan` is `normal`
or `full_unlock`. New accounts start with `normal` and a balance of `0`.
Existing accounts without these fields receive the same defaults when read by
the API, without a migration or default-field backfill.

Both fields are stored on the existing Better Auth `user` document and cannot
be supplied through signup or user profile updates. The API reads their current
values from MongoDB on every authenticated request, not from JWT claims.

Administrators can manually update either field or both:

```bash
curl -X PATCH http://localhost:8000/api/v1/admin/users/USER_ID/access \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan": "full_unlock", "balance": 100}'
```

The response is `{"plan": "full_unlock", "balance": 100}`. Omitting a field
leaves it unchanged. Empty bodies, null values, unknown fields, unknown plans,
and invalid balances return `422`. A balance must be an integer between `0`
and `9007199254740991`, inclusive, so the web client can represent it exactly.
An unauthenticated request returns `401`, a non-admin receives `403`, and an
unknown user returns `404`; this endpoint never creates users or changes roles.
Database outages or invalid stored access data return `503` rather than
granting access.

An absolute balance update returns `409` while the target account has reserved
chat coins. Plan-only updates remain allowed. This prevents balance assignments
from overwriting in-flight debits or refunds.

This is manual account management, not a payment or top-up API. Payments,
full-unlock expiration, and pricing for features other than chat are not defined.

## Coin redemption codes

The web creation form is available at `/admin/redeem-codes`, with a link in
the profile settings for administrators. Its server-rendered page checks the
current session and role before showing the form; the API checks them again
on submission. The form accepts a coin amount, code type and lifetime in days.

Administrators create a randomly generated code with
`POST /api/v1/admin/redeem-codes`. The body contains `coins` (a positive integer),
`kind` (`single_use` or `per_account`), and `expires_at` (a future ISO 8601 timestamp
with a timezone). For a three-day lifetime, set the deadline three days from now.
The `201` response includes the generated `code` and these three fields.

Signed-in users submit `{"code": "CODE"}` to
`POST /api/v1/account/redeem-code`. Leading/trailing spaces and letter case are
ignored. A successful response is `{"coins": 30}` for a 30-coin reward. The web
client refetches `/api/v1/me` through TanStack Query to update the shared balance.

- `single_use`: one redemption total, by one account.
- `per_account`: one redemption per account.
- Invalid or expired codes return `404`; already-used codes return `409`.
- Active chat reservations or balance overflow return `409` without consuming
  the code. Authentication and administrator checks use the existing middleware.

Codes expire at their deadline and are automatically removed by a MongoDB TTL
index. TTL cleanup can be delayed; the redemption query always checks the
deadline, so an expired code cannot be used while waiting for cleanup.

Code claims and balance credits use one MongoDB transaction. If either fails,
neither is saved. **Redemption requires a MongoDB replica set or sharded cluster;
standalone MongoDB returns `503`.** The current local standalone database must
be converted before this feature can be used locally. Never remove its data
volume during conversion. A separate one-node replica set can be used for tests:

```bash
CONVERSATION_HISTORY_STORE__URI='mongodb://localhost:27018/?directConnection=true' \
  uv run pytest tests/test_redeem_codes_api.py -q
```

## Chat pricing

`POST /api/v1/sessions/{session_id}/chat/stream` costs **3 coins per successful
user message** on the `normal` plan. `full_unlock` includes AI chat without
spending coins. The plan is checked from the live account when the request starts;
changing it during generation does not change that request's price.

For a new paid request, the server reserves 3 coins before starting AI generation.
`balance` is the available balance, excluding outstanding reservations. A normal
account with fewer than 3 available coins receives `402` with
`Not enough coins. AI chat costs 3 coins per message.` The AI does not run.
Rejected requests leave the conversation history unchanged. If a concurrent
reservation exhausts the balance, only that rejected request's new pending pair
is discarded. After topping up, the same idempotency key can be retried.

Successful completion means generation finished and the assistant message was
durably saved as `confirmed`. Only then is the reservation committed. AI errors,
cancellation or disconnects before completion return the reserved coins. A
disconnect after server-side completion does not reverse an already-completed
request; streaming cannot guarantee that the client received the final event.
Deleting the session or its chart profile while a reply is reserved does not
refund the reservation.

Replaying the same `Idempotency-Key` uses the existing message operation: it
never starts generation or reserves coins again, even if the balance is now zero.
Concurrent reservations cannot spend the same coins, and repeated refunds cannot
add coins twice. Reservations and settlement use conditional, single-user-document
updates, following [MongoDB's atomic update guarantees](https://www.mongodb.com/docs/manual/core/write-operations-atomicity/).

Outstanding reservations are stored as `chat_holds` on the existing user document;
there is no new collection or payment framework. On the next authenticated
request, the server checks these holds against the stored assistant messages:
confirmed messages and deleted sessions commit; failed, cancelled or missing
messages refund; pending messages keep their holds. Existing stale-message
cleanup marks abandoned pending messages failed after
`stale_pending_after_seconds` (15 minutes by default).
Recovery is lazy, not a background job. During database outages, a hold can remain
reserved until a later request can reconcile it. If finalization cannot be saved
but the refund succeeds, the message can remain pending until stale cleanup.

Other feature access is unchanged. No admin role exemption or free-chat quota is
added: chat pricing depends only on plan and coins.

## Build lá số example

```bash
curl -X POST http://localhost:8000/api/v1/laso/build \
  -H "Content-Type: application/json" \
  -d '{
    "day": 4,
    "month": 4,
    "year": 1998,
    "hour": 8,
    "gender": "M"
  }'
```

## Get the introductory Câu Phú

Send the birth data directly, using the same body as `POST /api/v1/laso/build`.
It matches the chart by cung Mệnh position, main stars, Tuần and Triệt, then
returns the original phú text from
`data/cung_menh_phu_luc_bat_v3_tieu_de_moi.json`.

```bash
curl -X POST http://localhost:8000/api/v1/laso/cau-phu \
  -H "Content-Type: application/json" \
  -d '{"day": 4, "month": 4, "year": 1998, "hour": 8, "gender": "M"}'
```

The response includes `tieu_de`, the unmodified four-line `cau_phu`, and the
same lines separately in `cac_cau`. No earlier build request is needed.

## Build sao lưu from birth data

`/api/v1/laso/build_sao_luu` takes:

- `birth_info`: the chart's birth data, with the same shape as `/laso/build`
- `observation_time`: same shape as build time (`day/month/year/hour/gender`)

Chart endpoints do not store a shared current chart. Each request calculates
its result from the supplied birth data, so requests from different users
cannot overwrite one another's chart.

```bash
curl -X POST http://localhost:8000/api/v1/laso/build_sao_luu \
  -H "Content-Type: application/json" \
  -d '{
    "birth_info": {
      "day": 4,
      "month": 4,
      "year": 1998,
      "hour": 8,
      "gender": "M"
    },
    "observation_time": {
      "day": 8,
      "month": 3,
      "year": 2026,
      "hour": 10,
      "gender": "M"
    }
  }'
```
