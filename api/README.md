# TuviLM API

FastAPI backend for TuviLM UI.

## Current status
- Real route: `POST /api/v1/laso/build`
- Real route: `POST /api/v1/chat/stream`
- Real route: `GET /api/v1/sessions`
- Real route: `GET /api/v1/sessions/{session_id}`
- Deprecated route: `POST /api/v1/laso/build_sao_luu`

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
docker compose up -d mongodb
```

```bash
uv run uvicorn api.main:app --reload --port 8000
```

The default MongoDB settings are suitable for the compose service:

```bash
MONGODB_URI=mongodb://localhost:27017/?replicaSet=rs0&directConnection=true
MONGODB_DB=tuvilm
MONGODB_TIMEOUT_MS=3000
```

MongoDB must be a replica set because chat persistence uses transactions. A
plain standalone `mongod` on port 27017 will not work with the default URI.

If the Mongo container exits unexpectedly, check:

```bash
docker compose ps
docker compose logs mongodb --tail=120
```

For local development, the compose file pins MongoDB to the stable `mongo:7.0`
image instead of the floating latest major. If you previously created the
volume with another MongoDB major and do not need that local data, reset it:

```bash
docker compose down -v
docker compose up -d mongodb
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
    "client_id": "local-browser-id",
    "display_name": "Người xem thử",
    "calendar": "solar",
    "date": 4,
    "month": 4,
    "year": 1998,
    "hour": 8,
    "minute": 30,
    "gender": "M"
  }'
```
