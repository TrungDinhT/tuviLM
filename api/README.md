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

Health, chart preview and chart casting remain public. The legacy anonymous
ID endpoint remains available, but `X-Anonymous-Owner-Id` no longer grants
access to saved profiles or chat. Existing anonymous data is not reassigned
to accounts automatically.

The web client resets chart and chat state when the active account changes.
Its persisted chart is restored only for the matching account. Requests from
the previous account are cancelled; private requests also check that their
fresh token belongs to the account that started them.

## Account plans and balance

Role and plan are separate: `role` is `user` or `admin`; `plan` is `normal`
or `full_unlock`. New accounts start with `normal` and a balance of `0`.
Existing accounts without these fields receive the same defaults when read by
the API, without a migration or read-time database writes.

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

This is manual account management, not a payment or top-up API. Balance units,
feature prices, charging, full-unlock expiration, and refunds are not defined
yet. Existing feature access is unchanged in this step.

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
