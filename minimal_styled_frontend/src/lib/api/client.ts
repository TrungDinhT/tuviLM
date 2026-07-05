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
  SessionChatStreamRequestSchema,
  type BuildLasoRequest,
  type BuildLasoResponse,
  type BuildSaoLuuRequest,
  type BuildSaoLuuResponse,
  type ChatResponse,
  type CreateAnonymousResponse,
  type CreateChartProfileRequest,
  type CreateChartProfileResponse,
  type CreateSessionRequest,
  type CreateSessionResponse,
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

export async function streamSessionChat(
  sessionId: string,
  req: SessionChatStreamRequest,
  ownerId: string,
  idempotencyKey: string,
  onTextDelta?: (delta: string) => void,
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

  return { answer: await readSessionChatStream(res, onTextDelta), tool_calls: [] };
}

async function readSessionChatStream(
  res: Response,
  onTextDelta?: (delta: string) => void,
): Promise<string> {
  let answer = '';
  const onEvent = (event: SessionChatEvent) => {
    if (event.type === 'text' && typeof event.delta === 'string') {
      answer += event.delta;
      onTextDelta?.(event.delta);
    }
    if (event.type === 'error') {
      throw { kind: 'stream', message: String(event.message || 'Luồng trò chuyện gặp lỗi.') } satisfies ApiError;
    }
  };

  if (!res.body) {
    parseSseEvents(await res.text(), onEvent);
    return answer;
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
  return answer;
}

interface SessionChatEvent {
  type?: unknown;
  delta?: unknown;
  message?: unknown;
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
