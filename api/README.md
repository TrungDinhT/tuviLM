# TuviLM API

FastAPI backend for TuviLM UI.

## Current status
- Real route: `POST /api/v1/laso/build`
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

## Build sao lưu

`/api/v1/laso/build_sao_luu` takes:
- `birth_info`: same shape as build time (`day/month/year/hour/gender`)
- `observation_time`: same shape as build time (`day/month/year/hour/gender`)

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
