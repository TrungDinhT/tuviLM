# Conversation History Persistence ADR

## Status

Accepted for V1 planning.

This is the principal architecture decision record for the conversation history
feature. Later implementation-ready documents in this folder should build from
the decisions captured here.

## Context

The conversation history layer needs to support a stateless FastAPI backend,
server owned conversation history, multiple chart profiles per anonymous user,
and a simple implementation path for V1.

An earlier design optimized for non-linear message trees. That design kept
sessions and messages in separate collections and relied on `parent_id` links to
model branches. It was flexible, but it introduced extra operational complexity
before the product needs true branching:

- more collections to coordinate
- more multi-document write paths
- more transaction and consistency concerns
- more complex history reconstruction
- database-specific tree traversal assumptions

For V1, the more useful constraint is speed and clarity: one chart profile can
have many linear chat sessions, and each session should carry the transcript
needed to reconstruct agent context.

## Decision

Use MongoDB for V1, with two primary collections:

- `chart_profiles`
- `sessions`

Keep `ChartProfile` and `Session` separate, but embed ordered messages directly
inside each `Session` document.

A `ChartProfile` is a reusable birth profile/person. It stores the owner
identity and the `birth_info` required to recompute the `LaSo` object. One
anonymous owner can have many chart profiles. Duplicate birth info is allowed;
idempotency prevents accidental duplicate records from retries, not intentional
duplicate profiles.

`birth_info` is the canonical durable input for the chart. The computed `LaSo`
object is derived state and is not stored as durable V1 data. A later
implementation may cache a computed `LaSo` snapshot for performance or
debugging, but that cache must remain disposable and rebuildable from
`birth_info`.

A `Session` is one linear conversation for one chart profile. It stores
`chart_profile_id` and embeds an ordered `messages[]` transcript. It does not
duplicate `owner_id` in V1; access flows through the associated chart profile.

V1 does not use a separate `messages` collection. V1 also does not model
`parent_id`, active leaves, branch tree traversal, or `$graphLookup`-style
history reconstruction.

Future branching should create a new `Session` copied up to the selected
message. This keeps the V1 mental model simple:

- one session equals one visible conversation thread
- one fork equals one new session
- old sessions remain unchanged

## Database Choice

MongoDB remains the V1 storage choice because the application benefits from a
document-oriented session aggregate during early development.

| Evaluation Criteria | MongoDB | PostgreSQL |
| --- | --- | --- |
| Development friction | Flexible document shape; lower migration overhead while the transcript model is still evolving. | Stronger schema discipline; migrations are required for structural changes. |
| Session transcript model | Natural fit for embedding ordered messages inside a session document. | Requires separate relational tables or JSONB to represent the same aggregate. |
| Data integrity | Mostly application-enforced; requires disciplined store logic. | Database-enforced constraints and foreign keys are stronger by default. |
| Future reporting and relational queries | Less natural for cross-profile relational reporting. | Strong fit for reporting, joins, and relational constraints. |
| Portability pressure | Good for V1 if MongoDB details stay behind a store boundary. | Viable later if the logical model is kept storage-agnostic. |

MongoDB is a storage choice, not a domain boundary. The API and agent
orchestration layers should not depend directly on MongoDB APIs, document
operators, or query semantics.

## Collection Model

At the ADR level, the model is described as logical aggregates rather than a
final serialized schema. Exact field types, validation shape, indexes, and
serialization formats belong in a later implementation-ready design.

### `ChartProfile`

A chart profile contains:

- an identifier
- `owner_id`
- display name
- `birth_info`
- timestamps

`birth_info` is the minimal persistent input required to recompute the `LaSo`
object on demand.

### `Session`

A session contains:

- an identifier
- `chart_profile_id`
- optional title or summary metadata
- timestamps
- embedded messages

Messages are embedded in chronological order. Each message carries its
identifier, role, content, message status, and timestamps. The session document
is the V1 aggregate used to load conversation context for the agent.

Soft deletion is the V1 deletion model for chart profiles and sessions. Deleting
a chart profile soft-deletes the profile and cascades soft deletion to its
sessions. Deleting a session soft-deletes only that session. Active streams are
not cancelled by deletion; already-reserved assistant messages may still
finalize into a soft-deleted session, but new normal reads and streams must
exclude soft-deleted profiles and sessions.

Soft-delete metadata is a persistence concern. Normal domain DTOs and HTTP
responses expose visible resources only and do not need to include `deleted_at`.

MongoDB's 16MB document limit is accepted for V1. If real usage approaches that
limit, later designs can introduce summarization, archiving, or extraction into
a separate message collection/table.

## Persistence Portability Constraint

The persistence layer should expose a narrow domain-level store/repository
boundary. The rest of the application should call operations such as:

- create anonymous owner identity
- create chart profile
- create session
- load session context
- reserve message pair for streaming
- update assistant message status/content

The exact Python protocols, repository classes, database libraries, indexes,
transactions, and migration mechanics are deferred to the implementation-ready
design.

The V1 implementation uses Beanie with PyMongo's async client behind this
boundary. That library choice remains an adapter detail rather than part of the
domain model.

The logical model should remain portable:

- MongoDB V1 can store a session aggregate as one document with embedded
  messages.
- PostgreSQL later can map the same aggregate to `chart_profiles`, `sessions`,
  and `messages` tables.

This portability constraint should not force premature abstraction. The goal is
only to prevent MongoDB-specific details from leaking into API handlers,
business logic, or agent orchestration.

## Streaming And Idempotency

The server owns conversation history. The client sends identifiers plus the
latest user message, not the full transcript.

The server issues persistent identifiers:

- anonymous owner id
- chart profile id
- session id
- message ids

The client stores the anonymous owner id and active profile/session ids locally.
The anonymous owner id is a V1 bearer-style identifier: it must be unguessable
and locally stored, but it is not full authentication.

Streaming uses reserve-then-stream:

1. Reserve the user message and assistant placeholder before generation.
2. Mark the user message `confirmed` immediately after reservation.
3. Mark the assistant placeholder `pending` while the model streams.
4. Mark the assistant message `confirmed`, `failed`, or `cancelled` when
   generation ends.

Idempotency applies to:

- chart profile creation
- session creation
- message append / streaming reservation

Idempotency prevents duplicate records from retries. It does not prevent a user
from intentionally creating multiple chart profiles with the same birth info.

For V1, idempotency metadata may live with the resources it protects instead of
in a separate idempotency ledger. If the system expands, idempotency behavior
becomes more complex, embedded metadata contributes to document-size pressure,
or other consistency needs appear, migrate idempotency to dedicated records and
reconsider transactions around idempotency/domain writes.

## Consequences

This design simplifies V1 persistence and removes the need for tree traversal in
the normal chat path. Loading session context is a single aggregate read plus a
chart profile lookup.

The tradeoff is that V1 gives up native in-place conversation branching. Future
branching duplicates history into a new session instead of sharing message nodes
between branches.

The design also accepts that some data integrity remains application-enforced in
MongoDB. The store layer must consistently validate chart profile/session
relationships, message statuses, soft deletion, and idempotency behavior.

## Deferred Decisions

- exact endpoint contracts
- exact repository/protocol definitions
- PostgreSQL library choice
- index definitions
- transaction mechanics for a future dedicated idempotency ledger
- retry response wire format
- auth and account-linking migration
- summarization strategy
- extracting messages into a separate collection/table if sessions approach
  MongoDB document limits
- vector search and semantic recall
