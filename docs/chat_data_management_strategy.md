# Chat Data Management Strategy

# 1. Executive Summary

This document outlines the architectural strategy for managing conversation and session data for the *Lá Số Tử Vi* AI-driven application. Based on a step-by-step evaluation of operational complexity, data integrity, data flexibility, and developer velocity, **MongoDB** has been selected as the primary database for V1.

The core architecture computes the `LaSo` stateful object on the fly from birth metadata stored in the session document. The database strictly manages chart profiles, conversation sessions, and message trees. The backend is designed to be stateless per API call, with MongoDB as the single source of truth for all persistent state.

---

# 2. Core Constraints & System Requirements

1. **Stateless Backend:** Each API call is self-contained. The `LaSo` object is recomputed on the fly from birth metadata stored in the session. No in-memory caching of chart state between requests.
2. **Non-Linear Conversations:** The system must support branching ("what-if") conversation architectures where users can fork a chat from any historical message point.
3. **Server-Owned History:** The server is the single source of truth for conversation history. The client sends only a `session_id` and the latest user message per request — not the full history.
4. **Horizontal Scalability:** The backend (Python/FastAPI) will scale horizontally across multiple instances to support concurrent user traffic.
5. **Developer Velocity:** The stack must minimize setup and maintenance friction during rapid prototyping and growth phases.

---

# 3. Database Comparison: MongoDB vs. PostgreSQL

| **Evaluation Criteria** | **MongoDB (NoSQL)** | **PostgreSQL (SQL)** |
| --- | --- | --- |
| **Development Friction** | High flexibility: schema-less document adjustments; no migrations required when evolving data structures. | High rigor: requires explicit table migrations (via Prisma/Alembic) for any structural modifications. |
| **Data Integrity** | Application-enforced: data constraints and consistency must be handled manually via backend code logic. | Database-enforced: rigid foreign keys and constraints actively block orphaned data at the storage layer. |
| **Tree-Like Queries** | Native traversal via `$graphLookup` aggregation. | Native traversal via SQL Recursive CTEs. |
| **Future Extensibility** | Native handling of deeply nested objects (e.g., dumping a complete `LaSo` snapshot directly into a session document). | Requires `JSONB` columns to mimic document-store flexibility. |
| **Concurrency Management** | Optimistic by default; requires explicit multi-document ACID transactions for safe horizontal scaling. | Pessimistic by default; uses row locking and automatic isolation levels. |

---

# 4. Collection Architecture & Tree-Branching Model

To safely scale data storage and completely eliminate the risk of hitting MongoDB's strict **16MB document size limit** over long histories, sessions and messages are decoupled into two distinct collections.

## 4.1. `chart_profiles` Collection

A `ChartProfile` represents a person's astrological chart. A single user may have multiple chart profiles (e.g. for different people), and each profile may have multiple conversation sessions.

```json
{
  "_id": "ObjectId",
  "display_name": "string",
  "birth_metadata": {
    "date": "string",
    "time": "string",
    "gender": "string"
  },
  "status": "active | deleted",
  "created_at": "datetime"
}
```

> `birth_metadata` is the minimal input required to recompute the `LaSo` object on the fly. The computed object itself is never stored.
> 

## 4.2. `sessions` Collection

A session represents a single conversation thread tied to a chart profile.

```json
{
  "_id": "ObjectId",
  "chart_profile_id": "ObjectId",
  "status": "active | deleted",
  "created_at": "datetime"
}
```

## 4.3. `messages` Collection

Each message belongs to a session. The `parent_id` field is the key structural decision that makes the message history a **tree**, not a flat array.

```json
{
  "_id": "ObjectId (server-generated)",
  "session_id": "ObjectId",
  "parent_id": "ObjectId | null",
  "role": "user | assistant",
  "content": "string",
  "status": "confirmed | failed",
  "created_at": "datetime"
}
```

**Why `parent_id`:**

- In the current linear conversation model, `parent_id` simply points to the previous message — structurally equivalent to a flat array, but future-proof.
- When forking is introduced, a new branch is created by pointing `parent_id` at any earlier message. No schema migration is required.
- Retrieving the active conversation path for a given leaf message is done by traversing `parent_id` links back to the root in application code.

---

# 5. API Contract & Data Flow

## 5.1. Request (Client → Server)

The client sends only the `session_id` and the new user message content. It does **not** send the full conversation history.

```json
{
  "session_id": "abc123",
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

**Phase 2 — Token Stream (subsequent chunks):**

```json
{ "type": "token", "delta": "Cung Mệnh..." }
{ "type": "token", "delta": " của bạn..." }
{ "type": "done", "status": "confirmed" }
```

The stream closes with a `done` event carrying the final message status. On failure, a `failed` event is emitted instead.

## 5.3. ID Generation

**The server generates all message IDs.** This keeps the server as the single source of truth and avoids coordination complexity from split ID ownership.

## 5.4. Session Key — Frontend Storage

The `session_id` is stored in **`localStorage`** on the client. This means:

- The session survives page refreshes
- No auth or user management is required in V1
- Multiple sessions per chart profile are supported naturally (store a list of session IDs keyed by `chart_profile_id`)

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

**UI rule:** Any interaction that depends on a stable message ID (fork, edit, retry) is **disabled while `status === "pending"`**. In practice, the pending window is the duration of the first stream chunk — typically imperceptible to the user.

## 6.3. Failure Handling

If the server emits a `failed` event mid-stream, the client marks the assistant message as `failed` and surfaces a retry action. A failed message cannot be used as a branch point for forking.

---

# 7. Engineering Discipline & Concurrency Guardrails

Because MongoDB treats collection relationships loosely, the engineering team must strictly enforce the following patterns in application code.

## 7.1. Soft Deletes as the Primary Safety Mechanism

Rather than hard-deleting sessions or messages, the system uses **soft deletes** (`status: "deleted"`). This eliminates the most common race condition — a user deleting a session while a stream is in progress — without requiring a transaction. The stream completes naturally; the client simply hides the session from the UI.

Hard deletes (physical removal from the DB) are a background cleanup task, not a synchronous operation.

## 7.2. Mandatory Multi-Document Transactions

For operations that span multiple collections — such as verifying a session is active before persisting an agent response, or cascading a soft delete across sessions and messages — **all writes must be explicitly wrapped in a MongoDB transaction.**

```python
async with await client.start_session() as mongo_session:
    async with mongo_session.start_transaction():
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
| Server restarts during stream | Partial assistant message in DB | `status: failed` set on incomplete messages at startup |

## 7.4. Out of Scope (Current Phase)

Advanced MongoDB Atlas features (vector search, serverless pipelines, semantic recall indexing) are explicitly out of scope. Context window management and message history selection are handled programmatically in the FastAPI application layer to keep infrastructure simple and cost-efficient.