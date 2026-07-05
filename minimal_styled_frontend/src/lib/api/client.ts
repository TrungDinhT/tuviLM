import { ZodError, type ZodType } from 'zod';
import type { ApiError } from '@/lib/http/errors';
import {
  BuildLasoRequestSchema,
  BuildLasoResponseSchema,
  BuildSaoLuuRequestSchema,
  BuildSaoLuuResponseSchema,
  ChatRequestSchema,
  ChatResponseSchema,
  CreateAnonymousResponseSchema,
  CreateChartProfileRequestSchema,
  CreateChartProfileResponseSchema,
  CreateSessionRequestSchema,
  CreateSessionResponseSchema,
  type BuildLasoRequest,
  type BuildLasoResponse,
  type BuildSaoLuuRequest,
  type BuildSaoLuuResponse,
  type ChatRequest,
  type ChatResponse,
  type CreateAnonymousResponse,
  type CreateChartProfileRequest,
  type CreateChartProfileResponse,
  type CreateSessionRequest,
  type CreateSessionResponse,
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

export function chat(req: ChatRequest): Promise<ChatResponse> {
  return call('/api/v1/chat', ChatRequestSchema, ChatResponseSchema, req);
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

/**
 * Re-thrown only when caller passes a malformed request — Zod errors at the
 * call site bubble up as ZodError, not `ApiError`. Keeps the request/response
 * error surfaces distinct.
 */
export { ZodError };
