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
export OPENROUTER_API_KEY="your-openrouter-api-key"
uv run uvicorn api.main:app --reload --port 8000
```

### Strength/weakness provider routing

The strength/weakness workflow uses `openrouter:deepseek/deepseek-v4.1-flash`
by default and calls OpenRouter with `OPENROUTER_API_KEY`.
Its requests restrict the upstream inference provider to Together using Pydantic
AI's `OpenRouterModelSettings`:

```json
{"provider": {"only": ["together"], "allow_fallbacks": false}}
```

This applies to both `POST /api/v1/laso/strength-weakness` and the workflow called
from chat. The chat and personality agents keep their normal OpenRouter routing.
A separate `TOGETHER_API_KEY` is not required.

Export `OPENROUTER_API_KEY` in the shell running the server. Putting the key only
in `.env` does not populate the environment read by Pydantic AI's provider.
Set `STRENGTH_WEAKNESS_MODEL` in the environment or `.env` to an
`openrouter:<model-id>` value, then restart the server. For example:

```bash
export STRENGTH_WEAKNESS_MODEL="openrouter:deepseek/deepseek-v4.1-flash"
```

The selected model must have a Together endpoint in OpenRouter's catalog.
As checked on 2026-10-27, `deepseek/deepseek-v4.1-flash` lists Together;
`qwen/qwen3.7-max` currently lists only Alibaba. Restricting a model without a
Together endpoint returns an OpenRouter error. Requests never fall back to
another provider.

References: [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection),
[Pydantic AI OpenRouter settings](https://pydantic.dev/docs/ai/models/openrouter/),
[DeepSeek V4.1 Flash endpoints](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash/endpoints),
and [Qwen3.7 Max endpoints](https://openrouter.ai/api/v1/models/qwen/qwen3.7-max/endpoints).

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
