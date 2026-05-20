# Backend Architecture

## Overview

The backend is a **FastAPI** service that computes Tử Vi birth charts and provides an AI-powered interpretation chat. It is structured into three layers: the REST API, the AI agent, and the chart engine.

```
api/                         src/agent/                    src/refactored/
┌──────────────┐           ┌─────────────────┐           ┌──────────────────────┐
│ FastAPI      │──uses──►  │ pydantic-ai     │──reads──► │ Chart Engine         │
│              │           │ Agent + Tools   │           │                      │
│ • REST routes│           │                 │           │ • LaSo (aggregate)   │
│ • DTO schemas│           │ • build_tuvi_   │           │ • TinhBan (placement)│
│ • Store      │           │   agent()       │           │ • Cung model         │
│   (contracts,│           │ • system prompt │           │ • Component catalog  │
│    mappers,  │           │ • tool defs     │           │ • Rule engine        │
│    mongo)    │           │                 │           │ • View builder       │
└──────┬───────┘           └─────────────────┘           └──────────────────────┘
┌──────▼───────┐
│  MongoDB     │
│  (PyMongo)   │
└──────────────┘
```

## API Layer (`api/`)

Exposes a REST API under `/api/v1/`:

| Endpoint                    | Method | Purpose                                    |
|-----------------------------|--------|--------------------------------------------|
| `/laso/build`               | POST   | Compute chart from birth data, create session |
| `/chat/stream`              | POST   | Stream AI response (SSE)                   |
| `/sessions`                 | GET    | List sessions for a client                 |
| `/sessions/{id}`            | GET    | Load session detail + messages             |
| `/sessions/{id}`            | DELETE | Soft-delete a session                      |
| `/health`                   | GET    | Health check                               |

**Key design decisions:**
- Stateless per request — the chart is recomputed from stored birth metadata on every call
- Server generates all message IDs; client sends anonymous `client_id`, `session_id`, and active-leaf `parent_id`
- SSE streaming protocol: `ids` (message IDs) → `text` (deltas) → `tool_call`/`tool_result` → `done`/`failed`
- MongoDB transactions for atomic multi-document writes

## AI Agent (`src/agent/`)

Built with **pydantic-ai**, configured for streaming. The agent is provided with a system prompt and tool definitions that give it structured access to the chart.

**Tools available to the agent:**
- Read cung by position (e.g. Tý, Sửu) or role (e.g. Mệnh, Quan Lộc)
- Search the Tử Vi Tân Biên reference book (segmented text with Whoosh full-text index)
- Find tam hợp (triple harmony) and xung chiếu (opposition) relationships
- Get role-specific analysis instructions from skill prompts

## Chart Engine (`src/refactored/`)

The core domain model that computes Tử Vi birth charts from birth data. Architecture is layered:

### Domain Model (`model/`)
- **LaSo**: Public aggregate root. Built from `LaSoPrior` (birth time/gender). Holds the chart and component catalog.
- **TinhBan**: Internal placement map. Stores natal placement + period layers. Queries: `position_of()`, `components_at()`, `cung_at()`.
- **Cung**: Query result representing one palace with its dia chi, thien can, role, and layered components.
- **PlacementLayer**: Immutable map of `ComponentId → DiaChi` for one layer context.

### Component Catalog (`components/`)
- Star definitions (Chính Tinh, Phụ Tinh, Tứ Hóa, Tuần Triệt, Vòng Tràng Sinh)
- Cung role definitions, cục definitions, star status maps (Đắc/Hãm)
- ComponentRepository for lookup by ID

### Placement Engine (`placement/`)
- **YAML-driven rule engine** for computing star positions
- Rules defined in `placement/rules/data/*.yaml` (chinh_tinh, phu_tinh, tu_hoa, etc.)
- Rule compiler, scopes, transforms, and resolver pipeline
- Supports absolute and relative positioning rules

### Assembly (`assembly/`)
- Orchestrates chart construction: natal assembly, period assembly, Tu Hoa Phai assembly
- Uses context objects (NatalContext, PeriodContext) as inputs to the placement engine

### View Layer (`view/`)
- Builds `LaSoView` and `CungView` DTOs from the domain model
- Converts internal component IDs to human-readable labels and data

## Data Persistence (`api/chat/`)

The chat store is layered to separate concerns:

| Layer | Path | Responsibility |
|-------|------|----------------|
| Contracts | `api/chat/contracts.py` | Domain types (`BirthInfo`, `Message`, `SessionInfo`) and `ChatStore` protocol |
| Mappers | `api/chat/mappers.py` | Domain ↔ DTO translation (the only module importing both `contracts` and `schemas`) |
| Documents | `api/chat/store/documents.py` | Pydantic MongoDB document models (`ChartProfileDocument`, `MessageDocument`, etc.) |
| Mongo Impl | `api/chat/store/mongo.py` | `MongoChatStore` — PyMongo async implementation of the `ChatStore` protocol |

Dependency flow: `schemas.py ← mappers.py ← main.py` and `contracts.py ← store/`. The store layer never imports from `api.schemas`.

MongoDB stores four collections:
- **chart_profiles**: Birth metadata (one per person charted)
- **sessions**: Chat sessions with `active_leaf_id` for conversation tree path
- **messages**: Tree-structured messages via `parent_id` links; status lifecycle: `streaming → confirmed/failed/cancelled`
- **tool_events**: Agent tool call/result audit trace

## Key Dependencies

| Library        | Purpose                       |
|----------------|-------------------------------|
| FastAPI        | Web framework                 |
| pydantic       | Data validation / DTOs        |
| pydantic-ai    | LLM agent framework           |
| PyMongo        | Async MongoDB driver          |
| PyYAML         | Rule file parsing             |
| lunarcalendar  | Lunar calendar conversion     |
| whoosh         | Full-text book index search   |
