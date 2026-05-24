# Conversation History Implementation Decisions

This document captures implementation decisions while the conversation history
plan is still being shaped. It is an input to the later implementation plan, not
the final implementation plan itself.

## Decision 1: Persistence Library And Boundary

Use Beanie for the MongoDB V1 adapter, but keep Beanie isolated behind a
storage-agnostic conversation history contract.

Planned module layout:

```text
api/chat/
  models.py          # storage-agnostic Pydantic models / DTOs
  contracts.py       # ConversationHistoryStore Protocol
  mongo/
    documents.py     # Beanie Document classes
    store.py         # BeanieConversationHistoryStore implementation
    mappers.py       # Beanie <-> domain model conversion
```

Rules:

- `api/chat/models.py` contains storage-agnostic Pydantic DTOs used by the
  conversation history contract and application code.
- `api/chat/contracts.py` exposes the `ConversationHistoryStore` protocol.
- `api/chat/mongo/documents.py` contains Beanie `Document` classes and other
  Mongo-specific persistence models.
- `api/chat/mongo/store.py` implements `ConversationHistoryStore` using Beanie.
- `api/chat/mongo/mappers.py` contains explicit conversions between Beanie
  documents and storage-agnostic DTOs.
- Beanie document classes must not escape `api/chat/mongo/`.
- API handlers and agent orchestration should depend on `api/chat/models.py` and
  `api/chat/contracts.py`, not direct MongoDB or Beanie APIs.
- Keep `api/schemas.py` for HTTP request/response schemas. Do not pass
  `api.schemas` request models directly into the store protocol; map API
  payloads to conversation history DTOs at the route/service boundary.

Rationale:

- Beanie gives convenient MongoDB document modeling for V1.
- A protocol boundary keeps MongoDB as an adapter detail rather than a domain
  boundary.
- A later PostgreSQL implementation can provide its own persistence models and
  implement the same `ConversationHistoryStore` contract.

## Decision 2: API Shape And Anonymous Owner Handling

Use explicit anonymous identity, chart profile, and session endpoints.

Anonymous owner creation is explicit:

- The client calls `POST /api/v1/anonymous` when no owner id is available in
  local storage.
- The server creates and returns a new anonymous owner id.
- The client stores the owner id locally and sends it on later requests.

Use a request header for anonymous owner identity:

```http
X-Anonymous-Owner-Id: anon_...
```

Do not pass `owner_id` in URL paths or query parameters for V1. The owner id is
a bearer-style identity token, not a product resource, so it belongs in request
metadata rather than resource paths.

Planned endpoint shape:

```text
POST /api/v1/anonymous

POST /api/v1/chart-profiles
GET  /api/v1/chart-profiles

POST /api/v1/chart-profiles/{chart_profile_id}/sessions
GET  /api/v1/chart-profiles/{chart_profile_id}/sessions

GET  /api/v1/sessions/{session_id}
POST /api/v1/sessions/{session_id}/chat/stream
```

Header behavior:

- `POST /api/v1/anonymous` does not require `X-Anonymous-Owner-Id`.
- All chart profile, session, and chat-history requests require
  `X-Anonymous-Owner-Id`.
- The server validates access through `Session -> ChartProfile -> owner_id`.

Profile creation, session creation, and chat stream requests should also use:

```http
Idempotency-Key: random-client-operation-id
```

Rationale:

- Anonymous identity has a clear lifecycle without coupling owner creation to
  chart profile creation.
- Chart profiles and sessions are real product resources, so they get explicit
  endpoints.
- Keeping owner identity out of URLs avoids treating it like a nested REST
  resource and leaves a cleaner path toward future `Authorization`-based auth.

## Decision 3: `birth_info` Shape

Use a storage-agnostic `BirthInfo` DTO in `api/chat/models.py`.

Conceptual shape:

```python
class BirthInfo(BaseModel):
    calendar: Literal["solar"] = "solar"
    year: int
    month: int
    day: int
    hour: int
    gender: Literal["M", "F"]
```

Rules:

- `birth_info` lives only on `ChartProfile`.
- `Session` never duplicates `birth_info`.
- `birth_info` is the canonical durable input used to recompute `LaSo`.
- The computed `LaSo` object is derived state and is not durable V1 storage.
- `study_year` / observation year is not part of `birth_info`.
- `study_year` belongs to transient request/session interactions when the user
  asks for a chart view for a specific year.
- Replace the current API `TuviTimePayload` with `BirthInfoPayload`.
- Use `day` only in the API and domain model. Do not keep temporary `date`
  compatibility.

Rationale:

- `calendar` makes the solar-calendar assumption explicit while leaving room for
  future calendar support.
- `day` is clearer than `date` because it names a date component, not a full
  calendar date.
- Keeping domain `BirthInfo` separate from `api.schemas.BirthInfoPayload`
  preserves the distinction between HTTP wire payloads and conversation history
  domain DTOs.

## Decision 4: Durable Message History Format

Persist only the visible chat transcript in V1.

A stored `ChatMessage` represents a user-visible message:

- message id
- role: user or assistant
- content
- status
- timestamps

Do not persist Pydantic AI native message objects, tool calls, tool results, or
streamed debug events in V1.

During a live stream, tool calls, tool results, and other debug events may still
be emitted to the frontend. The frontend may keep them in memory while the page
is alive, but they are not restored from durable conversation history after a
browser refresh.

When continuing a session from durable state, rebuild agent context from:

- `ChartProfile.birth_info`, used to recompute `LaSo`
- `Session.messages[]`, containing the visible transcript

Rationale:

- The visible transcript is the product-facing conversation history.
- Tool calls and Pydantic AI message parts are primarily debugging/trace data
  for V1.
- Avoiding native Pydantic AI history in storage keeps the model easier to
  render, migrate, and map to PostgreSQL later.

## Decision 5: Streaming Persistence And Terminal Message States

Use reserve-then-stream, but write assistant content to the database only once
per terminal stream outcome.

Message statuses:

- `pending`: reserved but not terminal yet
- `confirmed`: successfully completed
- `failed`: generation or server error, possibly with partial content
- `cancelled`: client cancelled or disconnected, possibly with partial content

Streaming write behavior:

1. Reserve the user message and assistant placeholder before generation.
2. Mark the user message `confirmed` immediately after reservation.
3. Create the assistant placeholder with empty content and status `pending`.
4. Accumulate streamed assistant text in server memory.
5. On success, write the full assistant content once and mark it `confirmed`.
6. On generation/server failure, write any partial assistant content once and
   mark it `failed`.
7. On client cancellation/disconnect, write any partial assistant content once
   and mark it `cancelled`.

Do not persist assistant content token by token in V1.

If a hard process crash leaves an assistant message stuck in `pending`, lazy
cleanup should run when the session is loaded. Stale pending assistant messages
older than the configured threshold should be marked `failed`.

Rationale:

- One final assistant write avoids excessive embedded-array updates during
  streaming.
- Persisting partial content on terminal failure/cancellation preserves what the
  user already saw.
- `cancelled` is distinct from `failed` because user/client interruption is not
  the same as model or server failure.
- Lazy cleanup is simpler than a startup job or background worker for V1.

## Decision 6: Idempotency

Use idempotency keys for mutation endpoints that create durable records or
reserve messages.

Require `Idempotency-Key` on:

- `POST /api/v1/chart-profiles`
- `POST /api/v1/chart-profiles/{chart_profile_id}/sessions`
- `POST /api/v1/sessions/{session_id}/chat/stream`

Do not require idempotency keys on `GET` requests.

Use resource-local idempotency metadata for V1 instead of a separate
`idempotency_records` collection.

For chart profile creation, store idempotency metadata on the created
`ChartProfile`:

- creation idempotency key
- creation request fingerprint/hash

For session creation, store idempotency metadata on the created `Session`:

- creation idempotency key
- creation request fingerprint/hash

For chat stream reservation, store operation metadata in the `Session` document
as a message operation registry rather than on every message:

- idempotency key
- request fingerprint/hash
- user message id
- assistant message id
- operation status

Scope keys by operation and owner/resource context, not globally:

- create chart profile: owner id + create profile operation + idempotency key
- create session: owner id + chart profile id + create session operation +
  idempotency key
- chat stream reservation: owner id + session id + append message pair operation
  + idempotency key

Store a request fingerprint for each idempotent operation. If the same scoped key
is reused with a different payload, reject it with `409 Conflict`.

Completed retry behavior:

- Create profile retry returns the original chart profile.
- Create session retry returns the original session.
- Chat stream retry after a terminal result returns the existing message ids and
  terminal assistant content/status without appending new messages.

Chat stream duplicate while original is still pending/in progress:

- Do not attach the second request to the original live stream in V1.
- Return/stream a structured duplicate-in-progress result that includes the
  reserved user and assistant message ids when available.
- The client can ignore the duplicate if it already knows those ids, or reload
  the session if it lost local stream state.

Example SSE event:

```json
{
  "type": "duplicate_in_progress",
  "user_message_id": "msg_user_123",
  "assistant_message_id": "msg_asst_456",
  "status": "pending"
}
```

Do not implement TTL cleanup for resource-local idempotency metadata in V1.
Creation and message operation metadata may remain with the resource for the
lifetime of that resource.

If the system expands, idempotency behavior becomes more complex, embedded
metadata contributes to document-size pressure, MongoDB's document size limit
becomes a concern, or another strong reason appears to separate idempotency from
domain state, migrate idempotency to dedicated records. At that time, reconsider
Mongo transactions for atomicity between idempotency records and domain writes.

Rationale:

- Idempotency prevents duplicate durable writes when the client retries after
  network drops, slow first chunks, browser retries, or double sends.
- For chat streaming, idempotency protects the message reservation, not the SSE
  transport itself.
- Resource-local metadata avoids a separate multi-document idempotency ledger in
  V1.
- The explicit anonymous owner endpoint means chart profile creation always has
  an owner id, so creation idempotency can be scoped directly to the owner.

## Decision 7: Store Responsibility Boundary

The `ConversationHistoryStore` contract should own persistence consistency
concerns, not just raw CRUD.

Store responsibilities:

- owner access checks
- idempotency enforcement for durable mutations
- chart profile creation/listing
- session creation/listing/loading
- session context loading with the associated chart profile
- message pair reservation for streaming
- assistant message finalization
- lazy cleanup of stale pending assistant messages when loading a session

Exact protocol method signatures are deferred to the implementation plan.

Rationale:

- Owner checks and idempotency need to stay close to the writes they protect.
- API handlers should orchestrate HTTP concerns, not duplicate persistence
  consistency rules.
- Future PostgreSQL support can implement the same consistency contract behind
  the same interface.

## Decision 8: Route Organization

Add a dedicated FastAPI router for conversation history endpoints rather than
putting all new endpoints directly in `api/main.py`.

Planned shape:

```text
api/chat/routes.py
```

`api/main.py` should include the router and keep application lifecycle setup.

Rationale:

- The feature is large enough to deserve its own route module.
- Keeping routes separate makes the transition from the current mocked/in-memory
  chat flow easier to understand.
- `api/main.py` should remain the app composition point rather than the home of
  all feature logic.

## Decision 9: Existing Endpoint Transition

Add the new conversation history endpoints first, beside the current endpoints.

Do not remove or replace the existing `/api/v1/laso/build`, `/api/v1/chat`, or
`/api/v1/chat/stream` endpoints in the first implementation pass unless the
frontend has already been rewired.

The implementation can then progressively adapt the frontend to use the new
profile/session/chat-history endpoints and retire mocked frontend behavior.

Rationale:

- The current frontend still depends on existing endpoints and contains mocked
  behavior for unsupported backend features.
- Adding the new endpoints first reduces migration risk.
- Rewiring the frontend can happen after the backend conversation history
  surface exists.

## Decision 10: Testing Strategy

Use two levels of tests:

- protocol/service-level tests with fake or in-memory store behavior where
  possible
- Mongo/Beanie adapter integration tests when a local test MongoDB is available

The implementation plan should define the exact test fixtures and commands.

Rationale:

- Store contract behavior should be testable without requiring MongoDB for every
  test.
- Beanie-specific mapping, indexes, and idempotency persistence still need
  adapter-level coverage.

## Decision 11: Soft Delete Scope

Implement soft delete for chart profiles and sessions in the first pass.

Use Beanie `DocumentWithSoftDelete` for:

- `ChartProfileDocument`
- `ChatSessionDocument`

Do not use `status: active | deleted` for chart profiles or sessions in V1.
Soft deletion is represented by `deleted_at`. Normal user-facing reads should
exclude soft-deleted documents.

Do not expose `deleted_at` in normal HTTP response schemas or storage-agnostic
DTOs. Soft-delete metadata is a persistence concern for V1; public APIs expose
only visible resources.

Keep message status separate:

```text
pending | confirmed | failed | cancelled
```

Add delete endpoints:

```text
DELETE /api/v1/sessions/{session_id}
DELETE /api/v1/chart-profiles/{chart_profile_id}
```

Session deletion:

- validates owner access through `Session -> ChartProfile -> owner_id`
- calls Beanie `.delete()` on the session document
- does not physically remove messages
- does not cancel an active stream

Chart profile deletion:

- validates owner access
- calls Beanie `.delete()` on the chart profile document
- explicitly cascades soft deletion to child sessions in the store
- does not use Beanie document hooks for cascade behavior
- does not require Mongo transactions for V1

Use explicit store logic for cascade deletion rather than document hooks.

Rationale:

- `DocumentWithSoftDelete` is designed for this use case and keeps deletion as a
  `deleted_at` timestamp instead of a vague resource status.
- Cascade deletion is application behavior and should remain visible in the
  store, not hidden in document hooks.
- Calling `.delete()` uses Beanie's soft-delete behavior directly and avoids
  relying on internal implementation details.
- Archive, if needed later, should be modeled separately from deletion, for
  example with `archived_at`.

## Decision 12: Local Docker Compose

Add a local `docker_compose.yaml` for development.

The compose setup should support MongoDB only for now:

- starting MongoDB locally
- providing a repeatable path for manual end-to-end testing
- allowing the API and frontend to keep running from local development commands

The exact services, ports, environment variables, and commands are deferred to
the implementation plan.

Rationale:

- Conversation history depends on a real database.
- A compose setup makes local manual testing less fragile.
- It gives a natural place to document the development workflow for the new
  persistence layer.

## Decision 13: Implementation Scope And Staging

The implementation plan should target a full vertical slice in one PR, but stage
the work internally so changes are easy to review.

Target the full vertical slice:

- MongoDB/Beanie setup
- storage-agnostic DTOs and store contract
- Mongo/Beanie adapter
- chart profile APIs
- session APIs
- persisted chat streaming endpoint
- visible transcript reconstruction for agent context
- tests

Stage the implementation in the plan:

1. dependencies, configuration, and local MongoDB compose setup
2. domain DTOs, store contract, Beanie documents, and mappers
3. profile/session store methods and APIs
4. persisted chat stream with message reservation/finalization
5. tests and manual verification

Use environment variables:

```text
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=tuvilm
```

Add Beanie/MongoDB dependencies to `pyproject.toml`.

For V1 persisted chat, reconstruct agent context from:

- visible transcript stored in `Session.messages[]`
- recomputed `LaSo` from `ChartProfile.birth_info`

Rationale:

- A full vertical slice makes the feature usable end to end.
- Internal staging keeps the PR understandable despite landing as one branch.
- Running only MongoDB in Docker keeps local app development simple.

## Decision 14: Conversation Route Schemas And Stream Path

Keep HTTP request/response schemas in `api/schemas.py` for now, including the
new conversation-history endpoints.

Planned chat module shape:

```text
api/chat/
  models.py          # storage-agnostic Pydantic models / DTOs
  contracts.py       # ConversationHistoryStore Protocol
  routes.py          # FastAPI router for conversation endpoints
  mongo/
    documents.py
    store.py
    mappers.py
```

Add the persisted stream endpoint beside the existing legacy stream endpoint:

```text
POST /api/v1/sessions/{session_id}/chat/stream
```

Do not remove the existing endpoint in the first pass:

```text
POST /api/v1/chat/stream
```

Rationale:

- Keeping all HTTP schemas in `api/schemas.py` is simpler for the current
  codebase.
- `api/chat/models.py` remains the storage-agnostic DTO boundary; routes map
  `api.schemas` payloads into those DTOs.
- The new persisted stream path is session-scoped and does not break existing
  frontend calls immediately.

## Decision 15: IDs, Timestamps, And Transaction Stance

Domain IDs are strings.

ID conventions:

- top-level Mongo documents may expose ObjectId values as strings
- embedded message ids use server-generated UUID strings
- anonymous owner ids use unguessable server-generated strings

Do not require a `msg_` prefix for message ids in V1.

Use timezone-aware UTC datetimes for all durable timestamps.

Do not require Mongo multi-document transactions for V1. Instead:

- use resource-local idempotency metadata
- use careful operation ordering
- use atomic single-document updates for embedded session messages
- store a message operation registry inside the session for chat stream
  reservation/retry behavior
- enforce a backend guard allowing at most one pending assistant message per
  session

The frontend should also block sending while a stream is active, but backend
enforcement is still required.

If idempotency behavior becomes more complex, resource-local metadata contributes
to document-size pressure, MongoDB's document size limit becomes a concern, or
production consistency needs increase, migrate idempotency to dedicated records.
At that time, revisit Mongo transactions and a replica-set local setup.

Rationale:

- Transactions add local MongoDB and Beanie complexity.
- Embedded messages keep the core message append as one session-document update.
- Resource-local idempotency plus operation correlation gives a recoverable V1
  consistency model without requiring transactions immediately.
