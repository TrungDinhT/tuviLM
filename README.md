# TuviLM

TuviLM makes a **Lá Số Tử Vi** (Vietnamese astrology chart) from a birth date
and hour. Users can then ask an AI agent questions about the chart. The agent
answers using the chart data and the book *Tử Vi Tân Biên*.

## Parts

The repo is a monorepo. The Python packages are one [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/).

| Folder | What it is | Tech |
| --- | --- | --- |
| `packages/tuvi-engine/` | Chart engine: places stars on the chart (`tuvi_engine`) | Python |
| `packages/tuvi-agent/` | AI agent and its tools (`tuvi_agent`) | pydantic-ai |
| `apps/api/` | Backend server: charts, chat, login (`tuvi_api`) | FastAPI, MongoDB |
| `apps/web/` | Web app | Next.js, React |
| `tools/` | `tuvi` and `tuvilm` CLIs, Streamlit tools (`tuvi_tools`) | Python |

## How it works

```text
Browser ──► Web app (:3000) ──/api/*──► API (:8000) ──► chart engine
                                          │    └──────► AI agent ──► LLM (OpenRouter)
                                          └───────────► MongoDB (accounts, sessions, charts, chats, coins)
```

1. The browser only talks to the web app. The web app forwards every `/api/*`
   request to the API (`apps/web/next.config.ts`).
2. The API gets a birth date, hour and gender. The chart engine builds the
   chart: `LaSo.from_prior(...)`. The web app draws it.
3. In chat, the agent calls tools to read the chart and the book, then answers.
   The answer streams to the browser. Chats are saved in MongoDB.
4. Casting a chart is open to everyone. Saved charts, chat and the strength and
   weakness report need an account. The API owns login: email and password
   (with email verification) or Google, and keeps the session in an httpOnly cookie.
5. AI chat and the strength and weakness report cost coins on the `normal` plan.
   Coins come from redeem codes that an administrator creates. See
   `apps/api/README.md`.

## Setup

You need: Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 20+,
[pnpm](https://pnpm.io), Docker, and an [OpenRouter](https://openrouter.ai) API key.

```bash
uv run tuvi setup     # install deps, create .env and apps/web/.env.local
# put OPENROUTER_API_KEY=sk-or-... in .env
uv run tuvi up        # MongoDB + API + web app; Ctrl+C stops all
```

Open http://localhost:3000. The API docs are at http://localhost:8000/docs.
More options are in `docs/local_development.md`.

To register locally, open the verification link that the API prints in the
`api` log: without Resend settings, the API does not send email.

The book files are not in git. The agent reads them from
`data/tuvitanbien_chunking_compact/part_2/`. Ask a maintainer for this folder.
Without it, charts work but the agent cannot read the book.

### If setup fails

**`'pnpm' is not on PATH`:** pnpm is not active in your shell. With mise, run
`mise use -g pnpm@11` (the lockfile is pnpm 11). Without mise, run `corepack enable pnpm`.

**Docker permission denied:** your user cannot use Docker. `tuvi up` prints the
fix and, in a terminal, asks whether to run the docker command with sudo this
time. Pick one:

- Add your user to the `docker` group, then open a new shell. This group gives
  root-level access to the machine.
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker      # or log out and log in
  docker ps          # must work without sudo
  ```
- Or run Docker with sudo: `uv run tuvi up --sudo`, and stop MongoDB with
  `uv run tuvi down --sudo`.
- Or run your own MongoDB on port 27017 and use `uv run tuvi up --no-db`.

**`uv: command not found`:** install uv: `mise use -g uv@latest`, or see
https://docs.astral.sh/uv/getting-started/installation/.

**Without the CLI:**

```bash
docker compose up -d --wait                                 # MongoDB (replica set)
export OPENROUTER_API_KEY=sk-or-...                         # only `tuvi up` reads it from .env
uv run uvicorn tuvi_api.main:app --reload --port 8000       # API, from the repo root
cd apps/web && pnpm install && pnpm dev                     # web app
```

## Folders

```text
apps/api/src/tuvi_api/          backend
  main.py                       app, chart routes
  auth/                         login, sessions, email, Google
  accounts/                     plans, coins, redeem codes, capability reports
  chat/                         chat routes and MongoDB store
packages/tuvi-engine/src/tuvi_engine/
  la_so.py                      main class: LaSo
  placement/rules/data/         where each star goes (YAML)
  components/data/              star and palace data (JSON)
  data/                         câu phú text
packages/tuvi-agent/src/tuvi_agent/
  main.py                       agent prompt and tool list
  tool/                         tools the agent can call
  tool/cach_cuc/data/           cách cục rules (YAML)
  workflow/                     sub-agents (personality/, strength_weakness/)
apps/web/src/
  app/                          pages
  features/                     UI for each page
  lib/api/                      calls to the backend
  lib/auth-client.ts            login calls and the session
tools/src/tuvi_tools/           tuvi CLI, cách cục editor, chart viewer
  workflow_cli/                 tuvilm: run workflows, view reports
docs/                           design docs
tests/                          Python tests
```

## Tests

```bash
uv run tuvi check     # Python tests + web typecheck, lint and tests
```

Tests that need MongoDB are skipped when it is not running. Start it with
`uv run tuvi up` or `docker compose up -d --wait` to run them. The redeem code
tests need the replica set from `docker-compose.yaml`.

There is no CI. Run the checks before you open a PR.

## How to contribute

**Change where a star goes:** edit the YAML files in
`packages/tuvi-engine/src/tuvi_engine/placement/rules/data/`. Add a test in
`tests/test_placement_*.py`. Read `docs/la_so_design/architecture/placement_rules.md` first.

**Add a cách cục (star pattern):** edit
`packages/tuvi-agent/src/tuvi_agent/tool/cach_cuc/data/cach_cuc_reviewed.yaml`,
or use the editor: `uv run tuvi editor`.
The rule format is in `docs/la_so_design/cach_cuc_condition_language.md`.

**Add an agent tool:**
1. Write a function in `packages/tuvi-agent/src/tuvi_agent/tool/`. It takes `RunContext[TuviAgentDeps]`.
2. Export it in `tool/__init__.py`.
3. Add it to `tools=[...]` in `packages/tuvi-agent/src/tuvi_agent/main.py`.

The tool should return chart data. The agent writes the explanation.

**Add a sub-agent:** follow `docs/agent_workflows/adding_a_workflow.md`.

**Add a page:** in `apps/web/`, add `src/app/<name>/page.tsx` and put the UI in
`src/features/<name>/`. Call the backend only through `src/lib/api/`.

**Add a Python dependency:** `uv add --package <tuvi-engine|tuvi-agent|tuvi-api|tuvi-tools> <dep>`.

**Rules:**
- The chart engine (`tuvi_engine`) has no network, database or AI calls.
- Code names use Vietnamese words without accents: `cung`, `sao`, `dia_chi`.
- Run all commands from the repo root.
- Fork the repo, make a branch, and open a PR to `main`.

## Docs to read

1. `docs/la_so_design/domain_context.md`: what a chart is
2. `docs/la_so_design/architecture/`: how the chart engine works
3. `docs/conversation_history/`: how chats are stored
4. `apps/api/README.md`: API routes, login and settings
5. `docs/local_development.md`: the `tuvi` CLI

## Words

| Word | Meaning |
| --- | --- |
| Lá số | The chart |
| Cung | One of 12 boxes on the chart. Each has a role: Mệnh (self), Tài Bạch (money), … |
| Địa Chi | The 12 positions (Tý to Hợi) |
| Thiên Can | The 10 heavenly stems |
| Sao | Star. Chính tinh = 14 main stars. Phụ tinh = minor stars. |
| Cục | Element from the Mệnh box. It decides where the star Tử Vi goes. |
| Bản mệnh | Element from the birth year |
| Tứ Hóa | Four changes: Lộc, Quyền, Khoa, Kỵ |
| Tuần / Triệt | Two marks that make a box weaker |
| Cách cục | A known star pattern with a meaning |
| Đại hạn / Tiểu hạn | 10-year period / 1-year period |
| Câu phú | A classic verse about the chart |
| Đắc / Hãm | Star in a good place / bad place |

## Workflow reports (`tuvilm`)

`tuvilm run` runs a workflow on a list of birth profiles and writes a YAML
report. Select the model with `--model`, before or after `run`:

```bash
uv run tuvilm --model openrouter:qwen/qwen3.8-flash run data/workflow_profiles.yaml --workflow strength_weakness
```

Without `--model`, the CLI uses `TUVILM_WORKFLOW_MODEL` or the default model.

`tuvilm view` opens a dashboard for the strength and weakness workflow:

```bash
uv run tuvilm view
```

The dashboard finds `reports/strength_weakness*.yaml` and `.yml` files. Select
more than one run in the sidebar, or upload more than one report, to compare
models. To open one report directly:

```bash
uv run tuvilm view reports/strength_weakness_qwen3.8-flash.yaml --port 8501
```

The dashboard has three parts:

- **Each profile:** the summary, strengths, weaknesses, reading and metrics of
  each profile, side by side for each model.
- **Tokens and time:** input, output, thinking, total, cache, requests, tool
  calls, batch time and the latency of each profile. Thinking is part of
  output. A missing metric shows as empty.
- **Diversity:** the number of different labels, the spread for each profile,
  the Jaccard index between profiles, the top-3 concentration, label
  frequency and an overlap matrix. The exact expected value applies when each
  profile keeps only 2 findings, so that list lengths stay the same.

The comparison uses only the profiles that succeeded in every report. It
matches them by name, birth date, birth hour and gender. Raw and normalized
numbers show separately. The normalized numbers are not calculated when a
profile has fewer than 2 findings. Diversity does not measure whether a
reading is correct.

Capabilities use the current ontology. Weakness themes use the reviewed
manual labels in `data/strength_weakness_review_annotations.json`. Before it
applies them, the viewer checks the SHA-256 of the report and the names of the
findings. The viewer can read a new report, but it shows no weakness theme
metrics until the report is reviewed and labeled. It does not guess a
difference in meaning from the names.

You can export the metric and diversity tables as CSV. The viewer only reads
files; it does not call a model.

More options are in `docs/cli/strength-weakness.md`.

## Bootstrap an administrator

Administrator access is granted by a private server-side script, not a public
signup option or API. The script promotes an existing account; it
does not create password hashes or change the account's plan, balance or email
verification status.

1. Register an account at `/register` using an email you control and a strong,
   unique password, then open the confirmation link sent to that email. The app
   does not let an unverified email/password account sign in.
2. On a trusted machine with private MongoDB access, run the script from the
   repository root. First check that the `.env` values `AUTH__MONGO_URI` and
   `AUTH__DATABASE_NAME` point to the database the API uses.

   ```bash
   uv sync
   uv run python -m tuvi_api.auth.bootstrap_admin --email admin@example.com
   ```

3. The script finds the account by email; you do not need to look up a user ID.
   Check the printed database, email and user ID, then type the full email to
   confirm. The script revokes existing sessions **before** granting the admin
   role. A missing account, duplicate email or cancelled confirmation does not
   change data. Email matching ignores leading/trailing spaces and letter case.
4. Sign in again and open `/admin/redeem-codes`, or use the admin link in your
   profile. Choose the coin amount, code type and lifetime to create a code.

The script never asks for or prints a password; use the password you registered.
An already-admin account is left unchanged. The script works on standalone
MongoDB as well as replica sets, without adding a dependency. Session revocation
and role promotion are separate writes: run it before using the new account,
without concurrent sign-ins. If a database write fails, inspect the account role
before retrying; sessions may already have been revoked.

Keep MongoDB private and authenticated in production. Never expose this script
through an HTTP route, run it during startup, or store database credentials in Git.

Coin redemption itself requires a MongoDB replica set; see the
[redemption requirements](apps/api/README.md#coin-redemption-codes).

## Known issues

- The login rate limit is kept in memory, so each API process counts on its own.
- A chart for a person younger than the first Đại Hạn, or a birth date in the
  future, fails with a 500 (issue #64).
