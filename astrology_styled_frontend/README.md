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
uv run uvicorn api.main:app --reload
```

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
