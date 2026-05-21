# tuviLM

Vietnamese Tử Vi (紫微斗數) astrology assistant.

## Repo layout

- `api/` — FastAPI backend. Run with `uv run uvicorn api.main:app --reload --port 8000`.
- `src/` — Python source for the Tử Vi engine (`refactored/`, `agent/`).
- `minimal_styled_frontend/` — **active frontend (Next.js 16 + shadcn/ui + Tailwind v4)**. All new frontend work lives here.
- `frontend/` — legacy prototype (Vite + React 18). Kept runnable for reference; do not invest further work here.
- `openspec/` — change proposals, specs, and design docs (see `openspec/changes/`).
- `docs/` — agent guides and architecture decision records.

## Frontend quickstart

```bash
cd minimal_styled_frontend
pnpm install
pnpm dev   # http://localhost:3000
```

The frontend talks to the FastAPI backend at `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).
