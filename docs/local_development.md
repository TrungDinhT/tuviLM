# Local development

All commands run from the repo root. You need `uv`, `pnpm` (Node 20+) and Docker.

```bash
uv run tuvi setup   # uv sync, pnpm install, create .env and apps/web/.env.local
uv run tuvi up      # MongoDB (Docker) + API on :8000 + web on :3000, logs in one terminal
uv run tuvi down    # stop MongoDB; the data volume is kept
uv run tuvi check   # Python tests + web typecheck, lint and tests
```

Open http://localhost:3000. The API docs are at http://localhost:8000/docs.

`Ctrl+C` stops the API and the web app together. If one of them exits, the other
stops too.

## Options

| Command | What it does |
| --- | --- |
| `tuvi up --no-db` | Do not start MongoDB with Docker. Use your own on port 27017. |
| `tuvi up --sudo` / `tuvi down --sudo` | Run the docker command with sudo |
| `tuvi up --api-only` / `--web-only` | Start one side only |
| `tuvi up --host 0.0.0.0` | Listen on the LAN, to open the app from a phone |
| `tuvi check --python-only` / `--web-only` | Run one side of the checks |
| `tuvi editor` | Streamlit editor for the cách cục rules |
| `tuvi viewer` | Streamlit chart viewer |

## Docker permission denied

If your user cannot use Docker, `tuvi up` and `tuvi down` print how to fix it.
In a terminal, they also ask whether to run the docker command with sudo this
time. To fix it for good, add your user to the `docker` group and open a new
shell. This group gives root-level access to the machine.

```bash
sudo usermod -aG docker $USER
```

## MongoDB

`docker-compose.yaml` runs MongoDB as a one-node replica set (`rs0`), because
coin redemption uses transactions. The first start sets up the replica set; the
data in the volume is kept. If an older standalone MongoDB is still running,
`tuvi up` uses it and warns you. Restart it with `uv run tuvi down`, then
`uv run tuvi up`. The redeem code tests need the replica set too.

## Environment

`tuvi up` reads the repo `.env` and passes it to the API, so you can keep
`OPENROUTER_API_KEY` there. Without it, charts work but the AI chat fails.
See `apps/api/README.md` for all API settings.

## Login emails

Without `AUTH__RESEND_API_KEY` and `AUTH__EMAIL_FROM`, the API does not send
email. It prints each verification and password reset email, with its link,
in the `api` log. Open the link to verify the account.

The web app forwards `/api/*` to `API_ORIGIN` (default `http://127.0.0.1:8000`).

## Book files

The agent's book files are not in git. Put them in
`data/tuvitanbien_chunking_compact/part_2/`, or set `BOOK_ROOT`. The tests that
need them are skipped when they are missing.
