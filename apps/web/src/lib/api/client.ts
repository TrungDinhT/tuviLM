import type { z } from "zod";

import { ApiErrorException } from "@/lib/http/errors";

import { clearAuthToken, getAuthHeaders } from "./auth-headers";

/**
 * The only place in the application that talks to the FastAPI backend.
 *
 * Three things happen here and nowhere else:
 * - requests go to same-origin `/api` paths, which Next forwards to FastAPI
 * - identity (`Authorization`) and idempotency headers are attached
 * - every response is parsed by a Zod schema and every failure is normalized
 *   to the `ApiError` union
 *
 * Components and hooks call the wrappers below; nothing calls `fetch` on the
 * backend directly.
 */

export interface RequestOptions<T> {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  schema: z.ZodType<T>;
  /**
   * Whether the request requires a signed-in account. Public chart building,
   * preview and health do not.
   */
  withAuth?: boolean;
  expectedUserId?: string | null;
  /**
   * Pass a stable key for anything that creates a resource or opens a stream.
   * Retrying the same logical operation must reuse the same key, or the
   * backend will create a duplicate.
   */
  idempotencyKey?: string;
  signal?: AbortSignal;
}

/** A fresh key for one logical operation. Reuse it across retries. */
export function newIdempotencyKey(): string {
  // `crypto.randomUUID` is secure-context-only: it is absent over plain HTTP
  // on a LAN (e.g. `http://192.168.1.23:3000`), where the chat still has to
  // work. The idempotency key needs uniqueness, not cryptographic strength,
  // so fall back to a timestamp + two random segments.
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `id-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;
}

export async function safeBody(response: Response): Promise<unknown> {
  const text = await response.text();
  if (text === "") return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

export async function request<T>(path: string, options: RequestOptions<T>): Promise<T> {
  const {
    method = "GET",
    body,
    schema,
    withAuth = false,
    expectedUserId,
    idempotencyKey,
    signal,
  } = options;

  const send = async (headers: Record<string, string>): Promise<Response> => {
    signal?.throwIfAborted();
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (idempotencyKey !== undefined) headers["Idempotency-Key"] = idempotencyKey;
    try {
      return await fetch(path, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        signal,
      });
    } catch (cause) {
      // An aborted request is the caller's own doing, not a network failure.
      if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
      throw new ApiErrorException({ kind: "network" });
    }
  };

  signal?.throwIfAborted();
  let response = await send(withAuth ? await getAuthHeaders(expectedUserId) : {});
  if (withAuth && response.status === 401) {
    // A cached token can outlive its session; retry once with a new one.
    clearAuthToken();
    response = await send(await getAuthHeaders(expectedUserId));
  }

  const payload = await safeBody(response);
  signal?.throwIfAborted();

  if (!response.ok) {
    throw new ApiErrorException({ kind: "http", status: response.status, body: payload });
  }

  const parsed = schema.safeParse(payload);
  if (!parsed.success) {
    throw new ApiErrorException({ kind: "parse", issues: parsed.error.issues });
  }

  return parsed.data;
}
