# TuviLM UI

Frontend app for:
- birth input
- lá số rendering
- cung analysis panel
- chatbot panel (streaming-style responses)

Current version uses a local dummy API (`src/api/mockApi.ts`).
You can later swap it to your real backend without changing UI layout/components.

## 1. Tech Stack

- React 18
- TypeScript
- Vite
- CSS (custom, no UI framework)
- `react-markdown` for analysis display

## 2. Prerequisites

- Node.js `>=20`
- npm `>=10`

Check:

```bash
node -v
npm -v
```

## 3. Install

From repository root:

```bash
cd frontend
npm install
```

## 4. Run in Development

```bash
npm run dev
```

Default URL: `http://localhost:5173`

Backend API default URL: `http://localhost:8000`

Optional override:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## 5. Build for Production

```bash
npm run build
```

Build output is generated in `frontend/dist`.

Preview production build locally:

```bash
npm run preview
```

## 6. Available Scripts

- `npm run dev`: start Vite dev server
- `npm run build`: type-check + build bundle
- `npm run preview`: serve built app locally

## 7. Project Structure

```text
frontend/
  index.html
  package.json
  tsconfig.json
  vite.config.ts
  src/
    main.tsx
    App.tsx
    styles.css
    types.ts
    api/
      mockApi.ts
    components/
      BirthForm.tsx
      LasoBoard.tsx
      AnalysisPanel.tsx
      ChatPanel.tsx
```

## 8. UI Behavior

### Input panel
- Enter birth info (day/month/year/hour/gender)
- Click `Lập lá số`

### Lá số panel
- Renders 12 cung in a board
- Each cung content is HTML from dummy data (compatible with backend `__repr__` style)
- Click a cung to load analysis

### Phân tích panel
- Shows markdown analysis for selected cung

### Chat panel
- Ask questions about current chart/selected cung
- Assistant message is rendered with chunked streaming effect

## 9. Dummy API Contract (Current)

File: `src/api/mockApi.ts`

- `buildLaso(input)` -> calls real backend `POST /api/v1/laso/build`
- `buildSaoLuu({ tinhBan, observationTime })` -> calls backend `POST /api/v1/laso/build_sao_luu`
- `getAnalysis(position)` -> returns markdown string
- `streamChatReply(messages, selectedPosition, onChunk)` -> chunked chat text

This mirrors the future backend flow, so migration is straightforward.

## 10. Integrate Real Backend Later

Recommended migration steps:

1. Keep UI components unchanged.
2. Replace internals of `src/api/mockApi.ts` with HTTP calls (`fetch`/`axios`).
3. Preserve function signatures:
   - `buildLaso`
   - `buildSaoLuu`
   - `getAnalysis`
   - `streamChatReply`
4. If backend supports SSE/WebSocket, map stream events to `onChunk`.

## 11. Common Issues

### Port already in use

Change Vite port in `vite.config.ts`:

```ts
server: { port: 5174 }
```

### `npm install` fails due to lock/cache

```bash
rm -rf node_modules package-lock.json
npm install
```

### Blank page after run

- Check browser console
- Confirm `http://localhost:5173`
- Re-run:

```bash
npm run dev
```

## 12. Dependencies

Runtime:
- `react`
- `react-dom`
- `react-markdown`

Dev:
- `typescript`
- `vite`
- `@vitejs/plugin-react`
- `@types/react`
- `@types/react-dom`
