# TuviLM API

FastAPI backend for TuviLM UI.

## Current status
- Real route: `POST /api/v1/laso/build`
- Real route: `POST /api/v1/laso/build_sao_luu`
- Dummy routes:
  - `POST /api/v1/laso/analyze`
  - `POST /api/v1/chat`

## Install dependencies
From repo root:

```bash
poetry install
```

or if you use pip directly:

```bash
pip install fastapi uvicorn pydantic
```

## Run server
From repo root:

```bash
poetry run uvicorn api.main:app --reload --port 8000
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
    "date": 4,
    "month": 4,
    "year": 1998,
    "hour": 8,
    "gender": "M"
  }'
```

## Build sao lưu from existing tinh ban

`/api/v1/laso/build_sao_luu` takes:
- `tinhBan`: an already-built `TinhBan` object
- `observation_time`: same shape as build time (`date/month/year/hour/gender`)

```bash
curl -X POST http://localhost:8000/api/v1/laso/build_sao_luu \
  -H "Content-Type: application/json" \
  -d '{
    "tinhBan": { "...": "existing tinh ban JSON" },
    "observation_time": {
      "date": 8,
      "month": 3,
      "year": 2026,
      "hour": 10,
      "gender": "M"
    }
  }'
```
