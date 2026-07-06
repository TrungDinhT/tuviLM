import { ZodError, type ZodType } from 'zod';
import type { ApiError } from '@/lib/http/errors';
import {
  BuildLasoRequestSchema,
  BuildLasoResponseSchema,
  BuildSaoLuuRequestSchema,
  BuildSaoLuuResponseSchema,
  CreateAnonymousResponseSchema,
  CreateChartProfileRequestSchema,
  CreateChartProfileResponseSchema,
  CreateSessionRequestSchema,
  CreateSessionResponseSchema,
  GetSessionResponseSchema,
  ListChartProfilesResponseSchema,
  ListSessionsResponseSchema,
  SessionChatStreamRequestSchema,
  type BuildLasoRequest,
  type BuildLasoResponse,
  type BuildSaoLuuRequest,
  type BuildSaoLuuResponse,
  type ChatDebugEvent,
  type ChatResponse,
  type ChatToolCall,
  type CreateAnonymousResponse,
  type CreateChartProfileRequest,
  type CreateChartProfileResponse,
  type CreateSessionRequest,
  type CreateSessionResponse,
  type GetSessionResponse,
  type ListChartProfilesResponse,
  type ListSessionsResponse,
  type SessionChatStreamRequest,
} from './schemas';

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function call<Req, Res>(
  path: string,
  requestSchema: ZodType<Req>,
  responseSchema: ZodType<Res>,
  body: Req,
  headers?: Record<string, string>,
): Promise<Res> {
  const parsedBody = requestSchema.parse(body);

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify(parsedBody),
    });
  } catch {
    throw { kind: 'network' } satisfies ApiError;
  }

  if (!res.ok) {
    throw { kind: 'http', status: res.status, body: await safeBody(res) } satisfies ApiError;
  }

  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw { kind: 'parse', issues: [] } satisfies ApiError;
  }

  const result = responseSchema.safeParse(raw);
  if (!result.success) {
    throw { kind: 'parse', issues: result.error.issues } satisfies ApiError;
  }
  return result.data;
}

async function postWithoutBody<Res>(
  path: string,
  responseSchema: ZodType<Res>,
): Promise<Res> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { method: 'POST' });
  } catch {
    throw { kind: 'network' } satisfies ApiError;
  }

  if (!res.ok) {
    throw { kind: 'http', status: res.status, body: await safeBody(res) } satisfies ApiError;
  }

  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw { kind: 'parse', issues: [] } satisfies ApiError;
  }

  const result = responseSchema.safeParse(raw);
  if (!result.success) {
    throw { kind: 'parse', issues: result.error.issues } satisfies ApiError;
  }
  return result.data;
}

async function get<Res>(
  path: string,
  responseSchema: ZodType<Res>,
  headers?: Record<string, string>,
): Promise<Res> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { headers });
  } catch {
    throw { kind: 'network' } satisfies ApiError;
  }

  if (!res.ok) {
    throw { kind: 'http', status: res.status, body: await safeBody(res) } satisfies ApiError;
  }

  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw { kind: 'parse', issues: [] } satisfies ApiError;
  }

  const result = responseSchema.safeParse(raw);
  if (!result.success) {
    throw { kind: 'parse', issues: result.error.issues } satisfies ApiError;
  }
  return result.data;
}

async function remove(path: string, headers?: Record<string, string>): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { method: 'DELETE', headers });
  } catch {
    throw { kind: 'network' } satisfies ApiError;
  }

  if (!res.ok) {
    throw { kind: 'http', status: res.status, body: await safeBody(res) } satisfies ApiError;
  }
}

async function safeBody(res: Response): Promise<unknown> {
  try {
    return await res.json();
  } catch {
    try {
      return await res.text();
    } catch {
      return null;
    }
  }
}

export function buildLaso(req: BuildLasoRequest): Promise<BuildLasoResponse> {
  return call('/api/v1/laso/build', BuildLasoRequestSchema, BuildLasoResponseSchema, req);
}

export function buildSaoLuu(req: BuildSaoLuuRequest): Promise<BuildSaoLuuResponse> {
  return call(
    '/api/v1/laso/build_sao_luu',
    BuildSaoLuuRequestSchema,
    BuildSaoLuuResponseSchema,
    req,
  );
}

export function createAnonymous(): Promise<CreateAnonymousResponse> {
  return postWithoutBody('/api/v1/anonymous', CreateAnonymousResponseSchema);
}

export function createChartProfile(
  req: CreateChartProfileRequest,
  ownerId: string,
  idempotencyKey: string,
): Promise<CreateChartProfileResponse> {
  return call(
    '/api/v1/chart-profiles',
    CreateChartProfileRequestSchema,
    CreateChartProfileResponseSchema,
    req,
    {
      'X-Anonymous-Owner-Id': ownerId,
      'Idempotency-Key': idempotencyKey,
    },
  );
}

export function listChartProfiles(ownerId: string): Promise<ListChartProfilesResponse> {
  return get('/api/v1/chart-profiles', ListChartProfilesResponseSchema, {
    'X-Anonymous-Owner-Id': ownerId,
  });
}

export function deleteChartProfile(chartProfileId: string, ownerId: string): Promise<void> {
  return remove(`/api/v1/chart-profiles/${encodeURIComponent(chartProfileId)}`, {
    'X-Anonymous-Owner-Id': ownerId,
  });
}

export function createSession(
  chartProfileId: string,
  req: CreateSessionRequest,
  ownerId: string,
  idempotencyKey: string,
): Promise<CreateSessionResponse> {
  return call(
    `/api/v1/chart-profiles/${encodeURIComponent(chartProfileId)}/sessions`,
    CreateSessionRequestSchema,
    CreateSessionResponseSchema,
    req,
    {
      'X-Anonymous-Owner-Id': ownerId,
      'Idempotency-Key': idempotencyKey,
    },
  );
}

export function listSessions(
  chartProfileId: string,
  ownerId: string,
): Promise<ListSessionsResponse> {
  return get(
    `/api/v1/chart-profiles/${encodeURIComponent(chartProfileId)}/sessions`,
    ListSessionsResponseSchema,
    { 'X-Anonymous-Owner-Id': ownerId },
  );
}

export function getSession(sessionId: string, ownerId: string): Promise<GetSessionResponse> {
  return get(`/api/v1/sessions/${encodeURIComponent(sessionId)}`, GetSessionResponseSchema, {
    'X-Anonymous-Owner-Id': ownerId,
  });
}

export function deleteSession(sessionId: string, ownerId: string): Promise<void> {
  return remove(`/api/v1/sessions/${encodeURIComponent(sessionId)}`, {
    'X-Anonymous-Owner-Id': ownerId,
  });
}

export async function streamSessionChat(
  sessionId: string,
  req: SessionChatStreamRequest,
  ownerId: string,
  idempotencyKey: string,
  onTextDelta?: (delta: string) => void,
  onDebugEvent?: (event: ChatDebugEvent) => void,
): Promise<ChatResponse> {
  const body = SessionChatStreamRequestSchema.parse(req);
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}/api/v1/sessions/${encodeURIComponent(sessionId)}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Anonymous-Owner-Id': ownerId,
        'Idempotency-Key': idempotencyKey,
      },
      body: JSON.stringify(body),
    });
  } catch {
    throw { kind: 'network' } satisfies ApiError;
  }

  if (!res.ok) {
    throw { kind: 'http', status: res.status, body: await safeBody(res) } satisfies ApiError;
  }

  const stream = await readSessionChatStream(res, onTextDelta, onDebugEvent);
  return {
    answer: stream.answer,
    tool_calls: stream.toolCalls,
    debug_events: stream.debugEvents,
  };
}

async function readSessionChatStream(
  res: Response,
  onTextDelta?: (delta: string) => void,
  onDebugEvent?: (event: ChatDebugEvent) => void,
): Promise<{ answer: string; toolCalls: ChatToolCall[]; debugEvents: ChatDebugEvent[] }> {
  let answer = '';
  const toolCalls: ChatToolCall[] = [];
  const debugEvents: ChatDebugEvent[] = [];
  const onEvent = (event: SessionChatEvent) => {
    if (event.type === 'text' && typeof event.delta === 'string') {
      answer += event.delta;
      onTextDelta?.(event.delta);
    }
    const debugEvent = toDebugEvent(event);
    if (debugEvent) {
      debugEvents.push(debugEvent);
      onDebugEvent?.(debugEvent);
      if (debugEvent.type === 'tool_call' && typeof debugEvent.name === 'string') {
        toolCalls.push({
          id: typeof debugEvent.id === 'string' || debugEvent.id === null ? debugEvent.id : undefined,
          name: debugEvent.name,
          arguments: debugEvent.arguments,
        });
      }
    }
    if (event.type === 'error') {
      throw { kind: 'stream', message: String(event.message || 'Luồng trò chuyện gặp lỗi.') } satisfies ApiError;
    }
  };

  if (!res.body) {
    parseSseEvents(await res.text(), onEvent);
    return { answer, toolCalls, debugEvents };
  }

  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += value;
    const parts = buffer.split(/\n\n+/);
    buffer = parts.pop() ?? '';
    for (const part of parts) parseSseEvents(part, onEvent);
  }
  if (buffer.trim()) parseSseEvents(buffer, onEvent);
  return { answer, toolCalls, debugEvents };
}

interface SessionChatEvent {
  type?: unknown;
  delta?: unknown;
  message?: unknown;
  id?: unknown;
  name?: unknown;
  arguments?: unknown;
  content?: unknown;
  output?: unknown;
}

function toDebugEvent(event: SessionChatEvent): ChatDebugEvent | null {
  if (event.type === 'tool_call') {
    return {
      type: 'tool_call',
      id: typeof event.id === 'string' || event.id === null ? event.id : undefined,
      name: typeof event.name === 'string' || event.name === null ? event.name : undefined,
      arguments: event.arguments,
    };
  }
  if (event.type === 'tool_result') {
    return {
      type: 'tool_result',
      id: typeof event.id === 'string' || event.id === null ? event.id : undefined,
      name: typeof event.name === 'string' || event.name === null ? event.name : undefined,
      content: event.content,
    };
  }
  if (event.type === 'result') {
    return { type: 'result', output: event.output };
  }
  return null;
}

function parseSseEvents(raw: string, onEvent: (event: SessionChatEvent) => void): void {
  const data = raw
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trim())
    .join('\n');
  if (!data) return;
  try {
    onEvent(JSON.parse(data));
  } catch (err) {
    if (err && typeof err === 'object' && 'kind' in err) throw err;
    throw { kind: 'parse', issues: [] } satisfies ApiError;
  }
}

/**
 * Re-thrown only when caller passes a malformed request — Zod errors at the
 * call site bubble up as ZodError, not `ApiError`. Keeps the request/response
 * error surfaces distinct.
 */
export { ZodError };
