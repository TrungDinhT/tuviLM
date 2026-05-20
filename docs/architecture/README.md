# TuviLM — System Architecture

TuviLM is a **Tử Vi (Vietnamese astrology) AI assistant**. Users input birth data, the system computes a chart ("lá số"), and an LLM agent interprets it through a streaming chat interface.

## High-Level Architecture

```
┌──────────────────────┐        HTTP/SSE        ┌──────────────────────┐
│   Frontend           │ ◄──────────────────────► │   Backend            │
│   (Next.js 16)       │   REST + SSE streaming  │   (FastAPI)          │
│                      │                         │                      │
│   • Entry form       │   POST /laso/build      │   • Chart computation│
│   • Chart rendering  │   POST /chat/stream     │   • AI agent (pydantic-ai)
│   • Chat panel       │   GET  /sessions        │   • REST API routes  │
│                      │                         │                      │
└──────────────────────┘                         └──────────┬───────────┘
                                                            │
                                                   ┌────────▼───────────┐
                                                   │   MongoDB           │
                                                   │   • chart_profiles  │
                                                   │   • sessions        │
                                                   │   • messages        │
                                                   │   • tool_events     │
                                                   └────────────────────┘
```

## Core Flow

1. User fills out birth data form → frontend POSTs to `/api/v1/laso/build`
2. Backend computes the Tử Vi chart from birth data using a YAML-driven rule engine
3. Chart + chat session persisted in MongoDB; response returned to frontend
4. User asks questions via chat → frontend POSTs to `/api/v1/chat/stream`
5. Backend loads chart, constructs agent context, streams AI response via SSE
6. Frontend renders streaming markdown in the chat panel alongside the chart

## Technology Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | Next.js 16, React 19, Tailwind 4  |
| Backend    | FastAPI, pydantic-ai              |
| Database   | MongoDB (replica set)             |
| AI Agent   | pydantic-ai (OpenAI-compatible)   |
| Testing    | pytest                           |

## Sub-Systems

- **Chart Engine** (`src/refactored/`): Rule-based computation of star placements across 12 cung, with support for natal and period layers.
- **AI Agent** (`src/agent/`): LLM-powered assistant with tools for chart lookup, book search, and relationship queries.
- **API Layer** (`api/`): FastAPI service exposing chart building, chat streaming, and session management.
- **Frontend** (`frontend/`): Next.js app with entry form, interactive chart, and streaming chat.
