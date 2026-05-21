import { ZodError, type ZodType } from 'zod';
import type { ApiError } from '@/lib/http/errors';
import {
  BuildLasoRequestSchema,
  BuildLasoResponseSchema,
  BuildSaoLuuRequestSchema,
  BuildSaoLuuResponseSchema,
  type BuildLasoRequest,
  type BuildLasoResponse,
  type BuildSaoLuuRequest,
  type BuildSaoLuuResponse,
} from './schemas';

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function call<Req, Res>(
  path: string,
  requestSchema: ZodType<Req>,
  responseSchema: ZodType<Res>,
  body: Req,
): Promise<Res> {
  const parsedBody = requestSchema.parse(body);

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(parsedBody),
    });
  } catch {
    throw { kind: 'network' } satisfies ApiError;
  }

  if (!res.ok) {
    let parsedBodyOut: unknown = null;
    try {
      parsedBodyOut = await res.json();
    } catch {
      try {
        parsedBodyOut = await res.text();
      } catch {
        parsedBodyOut = null;
      }
    }
    throw { kind: 'http', status: res.status, body: parsedBodyOut } satisfies ApiError;
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

/**
 * Re-thrown only when caller passes a malformed request — Zod errors at the
 * call site bubble up as ZodError, not `ApiError`. Keeps the request/response
 * error surfaces distinct.
 */
export { ZodError };
