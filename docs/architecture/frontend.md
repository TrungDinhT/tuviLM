# Frontend Architecture

## Overview

The frontend is a **Next.js 16** application using the **App Router** with **React 19**. It is a client-rendered SPA with two pages: a landing/entry form and a chart + chat view.

```
frontend/app/
├── page.tsx                  Route: "/" — Entry form
├── chart/page.tsx            Route: "/chart" — Chart + Chat
├── _components/              UI components (all "use client")
│   ├── EntryForm.tsx         Birth data form
│   ├── ChartView.tsx         Main page container
│   ├── Chart.tsx             SVG chart grid
│   ├── ChatPanel.tsx         Chat area (streaming)
│   ├── LeftRail.tsx          Chart + year controls
│   ├── RightRail.tsx         Detail cards
│   └── ...
├── _lib/                     Utilities & types
│   ├── types.ts              TypeScript interfaces
│   ├── schemas.ts            Zod validation
│   └── session-store.ts      localStorage wrappers
├── services/api/v1/          API client layer
│   ├── laso/build.ts         POST /laso/build
│   ├── chat/send.ts          POST /chat/stream
│   └── sessions.ts           GET /sessions
└── constants/                Static data
    ├── chart-layout.ts       Grid layout config
    └── stars.json            Star reference data
```

## Pages & Navigation

| Route    | Component     | Description                                             |
|----------|---------------|---------------------------------------------------------|
| `/`      | Entry form    | Hero pitch + birth info form (name, gender, date, time) |
| `/chart` | Chart + Chat  | Three-column layout: chart | chat | detail cards          |

Flow: User submits entry form → `POST /laso/build` → on success, `router.push("/chart")`.

## Layout (Desktop)

```
┌──────────┬───────────────────┬──────────┐
│ LeftRail │    ChatPanel      │ RightRail│
│          │                   │          │
│  Chart   │  Messages         │ Detail   │
│  + year  │  + input          │ card for  │
│  controls│                   │ selected │
│          │                   │ cung/sao │
└──────────┴───────────────────┴──────────┘
```

Mobile view collapses into a simplified single-column layout.

## API Communication

All API calls go to `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`). Uses `@tanstack/react-query` for server state.

| Service               | Endpoint              | Transport       | Hook                  |
|-----------------------|-----------------------|-----------------|-----------------------|
| Chart build           | POST `/laso/build`    | fetch (JSON)    | `useBuildLaso`        |
| Chat (streaming)      | POST `/chat/stream`   | fetch + SSE     | `useStreamChat`       |
| Session history       | GET `/sessions/:id`   | fetch (JSON)    | `useQuery`            |

**Chat streaming protocol:** The client opens a fetch to `/chat/stream`, reads the `ReadableStream`, and parses Server-Sent Events: `ids` (server-assigned message IDs), `text` (Markdown deltas), `tool_call`/`tool_result` (agent tool events), `done`/`failed`.

## State Management

No global state library. State is managed locally:

| Concern              | Mechanism                        |
|----------------------|----------------------------------|
| Server/API state     | `@tanstack/react-query`          |
| Session persistence  | `localStorage` (client UUID + session stash) |
| Form validation      | `zod` schemas                    |
| UI state             | React `useState` in container components |

**Optimistic updates:** User messages render instantly with a temporary ID. The server-assigned ID from the SSE `ids` event replaces it. Interactions dependent on stable IDs are disabled while `status === "pending"`.

## Key Dependencies

| Package             | Purpose                        |
|---------------------|--------------------------------|
| Next.js 16          | Framework, routing, Turbopack  |
| React 19            | UI components                  |
| @tanstack/react-query | Server state + mutations     |
| react-markdown      | Render AI responses            |
| zod                 | Form validation                |
| Tailwind CSS v4     | Styling                        |
| use-stick-to-bottom | Auto-scroll chat               |
