# Background workflows

This module keeps a chat or workflow running when the phone locks, the browser
loses its connection, or the user closes the app after submitting a request.

```text
Panel submits → API starts an independent asyncio.Task → saves result
Panel polls/reopens → reads the saved snapshot → renders progress or result
```

The API process must remain running. There is no separate worker, durable queue,
lease, checkpoint, automatic model retry, or recovery of execution after API restart.

## Run the API

The normal command is sufficient:

```sh
uv run uvicorn api.main:app --reload --port 8000
```

Settings:

| Environment setting | Default | Purpose |
| --- | --- | --- |
| `RUNS__CONCURRENCY` | `2` | Maximum simultaneous workflows per API process |
| `RUNS__POLL_SECONDS` | `0.5` | Check explicit cancellation in the API |
| `RUNS__TIMEOUT_SECONDS` | `900` | Maximum wait/execution time for a run |

Tasks waiting for a local execution slot appear as `queued`. They live only in
memory. API shutdown stops outstanding tasks; startup does not restart them.
A fixed expiry marks abandoned records failed on read so they cannot block a
resource forever. Completed results remain available in MongoDB.

## Code layout

- `background_runs.py`: task execution, progress and result models.
- `run_routes.py`: the four common HTTP endpoints below.
- `workflows.py`: chat/personality handlers and workflow registration.
- `chat/storage/store.py`: run persistence alongside the existing history store.
- Frontend `use-workflow-run.ts`: uses the existing TanStack Query provider for
  polling, retries, request cancellation on unmount, and focus/network refresh.

There is no separate run-store object or transport/session state machine in the UI.
New workflows use the same endpoints; they do not need their own submission route.

## Existing store

`MongoConversationHistoryStore` owns `insert_run`, `get_run`, `latest_run`,
`update_run`, and `cancel_run`. They use its `workflow_runs` collection and the
existing MongoDB client, database, index initialization, and shutdown. The
collection stores current status, progress and result; there is no event log.

## Shared API

All endpoints use `X-Anonymous-Owner-Id`. Submission requires `Idempotency-Key`.
Repeating a request with the same key and inputs returns the original run and
never reruns the model. Another active run for the same owner/resource returns 409.

| Endpoint | Purpose |
| --- | --- |
| `POST /api/v1/runs` | Submit `{ "workflow": "chat", "inputs": { ... } }`; return a snapshot with HTTP 202 |
| `GET /api/v1/runs?workflow=chat&resource_id=session:ID` | Discover the latest run when reopening a panel |
| `GET /api/v1/runs/{id}` | Read status and saved result |
| `POST /api/v1/runs/{id}/cancel` | Explicit Stop action |

Statuses are `queued`, `running`, `succeeded`, `failed`, `cancelled`. Snapshots
include `inputs`, `state.text`, `state.progress`, `state.metadata`, `result`, `error`,
and `seq` (revision). The UI replaces its view with the latest snapshot, preventing
duplicate text. The UI polls once per second while a run is active, then stops.
Network errors retry with backoff up to ten seconds; returning to the foreground
or coming online lets TanStack Query refresh the snapshot. Each HTTP request times out after fifteen
seconds so a lost connection cannot stall observation indefinitely.
There is no SSE connection, event parser, heartbeat, or stream replay in this API.

Among client actions, only explicit cancellation stops generation. Client disconnection and panel unmount
detach observation. Cancellation is accepted until result publication starts.

## Add a workflow with any output structure

Register an input model, ownership validator, handler, and optional output schema
in `registered_workflows()` in `api/workflows.py`:

```python
class ReportInputs(BaseModel):
    session_id: str

class ScoreRow(BaseModel):
    category: str
    score: float

class ReportOutput(BaseModel):
    rows: list[ScoreRow]
    recommendations: list[str]

async def authorize(owner_id, inputs):
    await history.load_session_context(owner_id, inputs.session_id)
    return f"report:{inputs.session_id}"

async def execute(context, inputs):
    await context.progress("Computing scores")
    return {"rows": [{"category": "career", "score": 0.8}],
            "recommendations": ["Explore options"]}

# Add to the registry:
"report": Workflow(ReportInputs, authorize, execute, output=ReportOutput)
# A root array can use output=TypeAdapter(list[ScoreRow]).
```

Results may be any JSON object, list, scalar, or null. `state.text` is optional;
structured workflows do not need an `answer` field. A schema validates the result
before it is marked successful. `context.text(delta)`, `context.progress(message)`,
and `context.emit("metadata", {...})` update the saved display state.

An optional `finalize(context, inputs)` publishes to another store. Read
`context.status`, `context.result`, and `context.error` for the outcome. Chat uses
this callback to save its user/assistant messages. Publication runs once; a failure
marks the run failed rather than restarting the model.

Panels submit through `POST /api/v1/runs` with the workflow name and inputs.
If a future feature needs a custom route, it can call
`request.app.state.run_service.submit(...)` and return `run.snapshot()`.

## Add a panel

```tsx
const reportSchema = z.object({
  rows: z.array(z.object({ category: z.string(), score: z.number() })),
  recommendations: z.array(z.string()),
});
const workflow = useWorkflowRun({
  workflow: "report",
  resourceId: sessionId ? `report:${sessionId}` : null,
  resultSchema: reportSchema,
});

workflow.start({ session_id: sessionId });
// Render workflow.result?.rows with your table component.
// Disable submission while workflow.loading || workflow.active.
// Explicit Stop: workflow.cancel(). Retry observation: workflow.retry().
```

The resource key must match the backend validator. The hook discovers saved runs
on mount, retains an unresolved submission's idempotency key, and refreshes saved
snapshots after network/foreground changes.
New panels reuse this behavior and supply their own renderer/schema.

Inputs are limited to 128 KB, progress updates to 32 KB, and state/result to 1 MB
each. Larger artifacts can be stored separately and returned as links.

The legacy `/sessions/{id}/chat/stream` endpoint keeps its existing background-task
protection for the older frontend. New panels use the shared run API.

## Verification

`tests/test_workflow_runs.py` uses local MongoDB and creates/removes uniquely named
`tuvilm_runs_test_*` databases. It tests disconnects, lost submission responses,
idempotency, cancellation, saved results, and structured outputs.

```sh
uv run pytest tests/test_workflow_runs.py -q
cd astrology_styled_frontend
pnpm test
pnpm typecheck
```
