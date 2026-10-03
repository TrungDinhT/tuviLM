# TuviLM API

FastAPI backend for TuviLM UI.

## Current status
- Real route: `POST /api/v1/laso/build`
- Real route: `GET /api/v1/laso/cau-phu`
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

`GET /api/v1/me` returns the authenticated `user_id` and `role`. Missing,
invalid or revoked credentials return `401`; an authenticated user lacking
an administrator role receives `403` from `require_admin`. Authentication
service outages return `503` rather than granting access.

Health, chart preview and chart casting remain public. The legacy anonymous
ID endpoint remains available, but `X-Anonymous-Owner-Id` no longer grants
access to saved profiles or chat. Existing anonymous data is not reassigned
to accounts automatically.

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

Call this route after `POST /api/v1/laso/build`. It matches the completed
chart by cung Mệnh position, main stars, Tuần and Triệt, then returns the
original phú text from
`data/cung_menh_phu_luc_bat_v3_tieu_de_moi.json`.

```bash
curl http://localhost:8000/api/v1/laso/cau-phu
```

The response includes `tieu_de`, the unmodified four-line `cau_phu`, and the
same lines separately in `cac_cau`. Calling it before building a chart returns
HTTP `409`.

## Build sao lưu from server state

`/api/v1/laso/build_sao_luu` takes:
- `observation_time`: same shape as build time (`day/month/year/hour/gender`)

```bash
curl -X POST http://localhost:8000/api/v1/laso/build_sao_luu \
  -H "Content-Type: application/json" \
  -d '{
    "observation_time": {
      "day": 8,
      "month": 3,
      "year": 2026,
      "hour": 10,
      "gender": "M"
    }
  }'
```
