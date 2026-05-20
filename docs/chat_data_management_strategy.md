# Chat Data Management Strategy

# 1. Executive Summary

This document outlines the architectural strategy for managing conversation and session data for the *Lá Số Tử Vi* AI-driven application. Based on a step-by-step evaluation of operational complexity, data integrity, data flexibility, and developer velocity, **MongoDB** has been selected as the primary database for V1.

The core architecture computes the `LaSo` stateful object on the fly from birth metadata stored in the chart profile document. The database strictly manages chart profiles, conversation sessions, message trees, and tool-event traces. The backend is designed to be stateless per API call, with MongoDB as the single source of truth for all persistent state.

---

# 2. Core Constraints & System Requirements

1. **Stateless Backend:** Each API call is self-contained. The `LaSo` object is recomputed on the fly from birth metadata stored in the chart profile. No in-memory caching of chart state between requests.
2. **Non-Linear Conversations:** The system must support branching ("what-if") conversation architectures where users can fork a chat from any historical message point.
3. **Server-Owned History:** The server is the single source of truth for conversation history. The client sends its anonymous `client_id`, a `session_id`, `parent_id`, and the latest user message per request — not the full history.
4. **Horizontal Scalability:** The backend (Python/FastAPI) will scale horizontally across multiple instances to support concurrent user traffic.
5. **Developer Velocity:** The stack must minimize setup and maintenance friction during rapid prototyping and growth phases.

---

# 3. Database Comparison: MongoDB vs. PostgreSQL

| **Evaluation Criteria** | **MongoDB (NoSQL)** | **PostgreSQL (SQL)** |
| --- | --- | --- |
| **Development Friction** | High flexibility: schema-less document adjustments; no migrations required when evolving data structures. | High rigor: requires explicit table migrations (via Prisma/Alembic) for any structural modifications. |
| **Data Integrity** | Application-enforced: data constraints and consistency must be handled manually via backend code logic. | Database-enforced: rigid foreign keys and constraints actively block orphaned data at the storage layer. |
| **Tree-Like Queries** | Native traversal via `$graphLookup` aggregation. | Native traversal via SQL Recursive CTEs. |
| **Future Extensibility** | Native handling of deeply nested objects (e.g., dumping a complete `LaSo` snapshot into a chart profile cache field). | Requires `JSONB` columns to mimic document-store flexibility. |
| **Concurrency Management** | Optimistic by default; requires explicit multi-document ACID transactions for safe horizontal scaling. | Pessimistic by default; uses row locking and automatic isolation levels. |

---

# 4. Collection Architecture & Tree-Branching Model

To safely scale data storage and completely eliminate the risk of hitting MongoDB's strict **16MB document size limit** over long histories, sessions and messages are decoupled into two distinct collections.

## 4.1. `chart_profiles` Collection

A `ChartProfile` represents a person's astrological chart. A single user may have multiple chart profiles (e.g. for different people), and each profile may have multiple conversation sessions.

```json
{
  "_id": "ObjectId",
  "client_id": "string",
  "display_name": "string",
  "birth_metadata": {
    "calendar": "solar | lunar",
    "date": "number",
    "month": "number",
    "year": "number",
    "hour": "number",
    "minute": "number",
    "gender": "M | F"
  },
  "status": "active | deleted",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

> `birth_metadata` is the canonical user input required to recompute the `LaSo` object on the fly. The derived `LaSoPrior` and computed chart object are not stored as authoritative state. A future full-chart snapshot should be treated as a cache with an explicit schema version.
> 

## 4.2. `sessions` Collection

A session represents a single conversation thread tied to a chart profile.

```json
{
  "_id": "ObjectId",
  "client_id": "string",
  "chart_profile_id": "ObjectId",
  "active_leaf_id": "ObjectId",
  "status": "active | deleted",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

`active_leaf_id` stores the server-owned visible branch for the session. The message tree can contain hidden branches, but the current UI renders the path ending at this leaf.

## 4.3. `messages` Collection

Each message belongs to a session. The `parent_id` field is the key structural decision that makes the message history a **tree**, not a flat array.

```json
{
  "_id": "ObjectId (server-generated)",
  "session_id": "ObjectId",
  "parent_id": "ObjectId | null",
  "role": "user | assistant",
  "content": "string",
  "status": "confirmed | streaming | failed | cancelled | deleted",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Why `parent_id`:**

- In the current linear conversation model, `parent_id` simply points to the previous message — structurally equivalent to a flat array, but future-proof.
- When forking is introduced, a new branch is created by pointing `parent_id` at any earlier message. No schema migration is required.
- Retrieving the active conversation path for a given leaf message is done by traversing `parent_id` links back to the root in application code.

## 4.4. `tool_events` Collection

Tool calls and tool results are persisted separately from the chat transcript. They are trace/audit data, not core user-visible conversation state.

```json
{
  "_id": "ObjectId",
  "session_id": "ObjectId",
  "message_id": "ObjectId",
  "type": "tool_call | tool_result",
  "tool_call_id": "string | null",
  "name": "string | null",
  "payload": "object",
  "created_at": "datetime"
}
```

The live frontend still shows streamed tool chips. After refresh, V1 restores message text only; tool-event replay is reserved for a future debug/audit view.

---

# 5. API Contract & Data Flow

## 5.1. Request (Client → Server)

The client sends its anonymous `client_id`, the `session_id`, the `parent_id` it is replying to, and the new user message content. It does **not** send the full conversation history.

```json
{
  "client_id": "anonymous_browser_id",
  "session_id": "abc123",
  "parent_id": "message_id_current_leaf",
  "content": "Cung Mệnh của tôi có ý nghĩa gì?"
}
```

The server is responsible for:

1. Retrieving the full message history for the session from MongoDB
2. Retrieving `birth_metadata` from the associated `ChartProfile`
3. Recomputing the `LaSo` object from `birth_metadata`
4. Constructing the full context for the AI agent

## 5.2. Response — Streaming Protocol (Server → Client)

The server streams the response in chunks over a single persistent connection. The protocol is split into two phases:

**Phase 1 — ID Assignment (first chunk):**

```json
{
  "type": "ids",
  "user_message_id": "server_assigned_id_for_user_msg",
  "assistant_message_id": "server_assigned_id_for_assistant_msg"
}
```

This chunk is emitted immediately after the server persists the user message, before the agent begins generating. The client uses this to replace its temporary ID and unlock message-level UI interactions.

**Phase 2 — Text Stream (subsequent chunks):**

```json
{ "type": "text", "delta": "Cung Mệnh..." }
{ "type": "text", "delta": " của bạn..." }
{ "type": "done", "status": "confirmed" }
```

The stream closes with a `done` event carrying the final message status. On failure, a `failed` event is emitted instead. `text` is intentionally used instead of `token` because streamed deltas are chunks of text, not guaranteed model tokens.

## 5.3. ID Generation

**The server generates all message IDs.** This keeps the server as the single source of truth and avoids coordination complexity from split ID ownership.

## 5.4. Session Key — Frontend Storage

An anonymous `client_id` and the latest `session_id` are stored in **`localStorage`** on the client. This means:

- The session survives page refreshes
- No auth or user management is required in V1
- Multiple sessions per chart profile are supported naturally (store a list of session IDs keyed by `chart_profile_id`)
- The browser stores durable pointers only; MongoDB remains the source of truth for chart and message data

---

# 6. Client-Side State Management

## 6.1. Temporary Message IDs

Because the server generates all IDs asynchronously via the stream, the client assigns a **temporary local ID** to a user message at render time. This is replaced with the server-assigned ID when the first stream chunk (`type: ids`) arrives.

## 6.2. Message Status

Every message on the client carries a `status` field:

| Status | Meaning |
| --- | --- |
| `pending` | Sent to server, awaiting ID confirmation |
| `confirmed` | Server has assigned a real ID |
| `failed` | Server returned an error |
| `cancelled` | Stream was interrupted by client disconnect/abort |

**UI rule:** Any interaction that depends on a stable message ID (fork, edit, retry) is **disabled while `status === "pending"`**. In practice, the pending window is the duration of the first stream chunk — typically imperceptible to the user.

## 6.3. Failure Handling

If the server emits a `failed` event mid-stream, the client marks the assistant message as `failed`. The persisted session leaf moves to the confirmed user message so the question remains visible after reload and the next send can continue from there. A failed assistant message cannot be used as a branch point for forking.

---

# 7. Engineering Discipline & Concurrency Guardrails

Because MongoDB treats collection relationships loosely, the engineering team must strictly enforce the following patterns in application code.

## 7.1. Soft Deletes as the Primary Safety Mechanism

Rather than hard-deleting sessions or messages, the system uses **soft deletes** (`status: "deleted"`). This eliminates the most common race condition — a user deleting a session while a stream is in progress — without requiring a transaction. The stream completes naturally; the client simply hides the session from the UI.

Hard deletes (physical removal from the DB) are a background cleanup task, not a synchronous operation.

## 7.2. Mandatory Multi-Document Transactions

For operations that span multiple collections — such as verifying a session is active before persisting an agent response, or cascading a soft delete across sessions and messages — **all writes must be explicitly wrapped in a MongoDB transaction.**

```python
async with client.start_session() as mongo_session:
    async with await mongo_session.start_transaction():
        # 1. Verify session exists and is active within snapshot isolation
        session_doc = await db.sessions.find_one(
            {"_id": session_id, "status": "active"},
            session=mongo_session
        )
        if not session_doc:
            raise ValueError("Session has been deleted or does not exist.")

        # 2. Safely persist the user message
        await db.messages.insert_one(message_payload, session=mongo_session)
```

Omitting the `session=` parameter from any DB operation inside a transaction silently removes the safety net, risking orphaned documents and corrupted AI context under concurrent load.

## 7.3. Concurrency Scenarios & Mitigations

| Scenario | Risk | Mitigation |
| --- | --- | --- |
| User deletes session during active stream | Orphaned messages written after session deletion | Soft delete: stream finishes, session hidden from UI |
| User sends two messages simultaneously | Both read same parent, create unintended fork | Optimistic insert with `parent_id` check; treat as fork if detected |
| Server restarts during stream | Partial assistant message in DB | `status: failed` set on stale `streaming` assistant messages at startup |
| Client disconnects during stream | Assistant message remains incomplete | Store assistant message as `cancelled` |

## 7.4. Out of Scope (Current Phase)

Advanced MongoDB Atlas features (vector search, serverless pipelines, semantic recall indexing) are explicitly out of scope. Context window management and message history selection are handled programmatically in the FastAPI application layer to keep infrastructure simple and cost-efficient.

---

# 8. V1 Implementation Decisions & Trade-Offs

This section records decisions made during implementation planning that were not explicit in the original strategy.

## 8.1. Persistence Entry Point

`POST /api/v1/laso/build` creates:

1. a `chart_profiles` document
2. a `sessions` document
3. a stored root assistant greeting message

This matches the existing frontend flow: one entry form submit leads to the chart page and an immediately usable chat session. The trade-off is that users who only create a chart and never chat still create an empty session. This is acceptable for V1 because it avoids a second frontend orchestration step.

## 8.2. Anonymous Browser Identity

V1 uses a generated `client_id` stored in `localStorage` instead of auth. The backend scopes chart profiles and sessions by `client_id`.

Trade-off:

- Simple and good enough for a prototype.
- Not secure identity. Anyone with the browser storage or session IDs can act as that anonymous client.
- Future auth should replace or link this anonymous identity.

## 8.3. Local Development Runtime

The repo includes Docker Compose for MongoDB with a single-node replica set. This is needed because MongoDB transactions require a replica set, even for local development.

The backend is still configured by environment variables:

```bash
MONGODB_URI=mongodb://localhost:27017/?replicaSet=rs0&directConnection=true
MONGODB_DB=tuvilm
```

Trade-off:

- Docker Compose makes local full-app development predictable.
- Env-driven configuration still allows Atlas or another MongoDB deployment later.

## 8.4. Driver & Data Access Layer

The implementation uses PyMongo async directly behind small repository/service boundaries and Pydantic DTOs. It does not use Motor or an ODM.

Reasoning:

- Motor is no longer the preferred direction for new async MongoDB Python work.
- Explicit repositories make transactions, `session=` propagation, and message-tree queries visible.
- No ODM avoids a new abstraction layer while the schema is still evolving.

Trade-off:

- More manual mapping between MongoDB documents and API DTOs.
- Less framework magic; easier to debug during early architecture work.

## 8.5. Canonical Birth Metadata

The canonical stored chart input is the original user form: display name, calendar, date/month/year, hour/minute, and gender.

The implementation does **not** store `LaSoPrior` as persistent source of truth because it is derived data. If conversion logic changes, the source input remains clean.

Current limitation:

- V1 visibly supports solar/Dương only.
- Lunar/Âm input is rejected or disabled until lunar conversion semantics, including leap-month policy, are implemented deliberately.

## 8.6. Session History Loading

History browsing and session opening are separate:

- `GET /api/v1/sessions` returns lightweight summaries for the history drawer.
- `GET /api/v1/sessions/{session_id}` returns one session, chart profile, chart payload, and the active path messages.

The detail response includes `messages` and `has_more_before` so it can evolve into cursor pagination later without renaming the core field.

## 8.7. Branching Scope

The backend accepts `parent_id`, so the message tree is branch-ready. In V1, the backend requires `parent_id` to equal the session's `active_leaf_id`; stale parents return `409 Conflict`. Visible fork/edit/retry branch controls are intentionally deferred.

Trade-off:

- The storage model supports future non-linear chat.
- V1 UX remains linear and simpler to reason about.

## 8.8. Assistant Message Lifecycle

On chat send, the server transactionally inserts:

1. the confirmed user message
2. an assistant placeholder with `status: "streaming"`

The assistant message is updated to:

- `confirmed` after successful model completion
- `failed` after model/tool/storage failure
- `cancelled` after client disconnect/abort

For `failed` and `cancelled`, the session `active_leaf_id` is moved to the user message that the assistant was answering. This preserves the visible failed turn after reload while keeping successful turns anchored on the confirmed assistant response.

The backend may use the agent's final result event internally as a completion signal, but the frontend stream does not expose a separate `result` event because it would duplicate accumulated `text` chunks.

## 8.9. Transaction Granularity

Transactions are used for multi-document correctness boundaries:

- chart profile + session + root greeting creation
- user message + assistant placeholder insertion
- assistant finalization and session `active_leaf_id` update
- soft-deleting a session and its messages

Text streaming happens outside transactions. This avoids long-running transactions while the model is generating.

## 8.10. Known Follow-Up Work

- Migrate `/api/v1/laso/build_sao_luu` to session-backed chart state. It currently returns `410 Gone`.
- Add true lunar/Âm input support before enabling the selector again.
- Add visible fork/edit/retry UI and rules for failed-message retry.
- Add optional tool-event replay/debug UI.
- Add Mongo integration tests once Docker is available in the development/test environment.
