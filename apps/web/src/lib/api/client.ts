import { Result, type Schema } from "effect";

import { ApiErrorException } from "@/lib/http/errors";
import { validate } from "@/lib/schema";


/**
 * The only place in the application that talks to the FastAPI backend.
 *
 * Three things happen here and nowhere else:
 * - requests go to same-origin `/api` paths, which Next forwards to FastAPI
 * - idempotency headers are attached (the session cookie goes along by itself)
 * - every response is decoded by an Effect schema and every failure is normalized
 *   to the `ApiError` union
 *
 * Components and hooks call the wrappers below; nothing calls `fetch` on the
 * backend directly.
 */

export interface RequestOptions<T> {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  schema: Schema.ConstraintDecoder<T>;
  /**
   * Whether the request requires a signed-in account. Public chart building,
   * preview and health do not. The session cookie decides who the API sees.
   */
  withAuth?: boolean;
  /**
   * The account that started the request (from the account scope). `null`
   * means signed out: an account request then fails here, without a round trip.
   */
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
  if (withAuth) assertSignedIn(expectedUserId);
  const response = await send(expectedUserHeader(expectedUserId));

  const payload = await safeBody(response);
  signal?.throwIfAborted();

  if (!response.ok) {
    throw new ApiErrorException({ kind: "http", status: response.status, body: payload });
  }

  const decoded = validate(schema, payload);
  if (Result.isFailure(decoded)) {
    throw new ApiErrorException({ kind: "parse", issues: decoded.failure });
  }

  return decoded.success;
}

/**
 * The account this page was loaded for. The API refuses the request if the
 * session cookie belongs to someone else, e.g. after a sign-in in another tab.
 */
export function expectedUserHeader(expectedUserId: string | null | undefined): Record<string, string> {
  return expectedUserId ? { "X-Expected-User-Id": expectedUserId } : {};
}

/** An account request made while signed out fails without a round trip. */
export function assertSignedIn(expectedUserId: string | null | undefined): void {
  if (expectedUserId === null) {
    throw new ApiErrorException({
      kind: "http",
      status: 401,
      body: { detail: "Authentication required" },
    });
  }
}
