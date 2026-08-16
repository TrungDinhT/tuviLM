import type { z } from "zod";

import { env } from "@/config/env";
import { ApiErrorException } from "@/lib/http/errors";

import { getOwnerId } from "./owner";
import { createAnonymousResponseSchema } from "./schemas";

/**
 * The only place in the application that talks to the FastAPI backend.
 *
 * Three things happen here and nowhere else:
 * - the base URL is applied
 * - identity (`X-Anonymous-Owner-Id`) and idempotency headers are attached
 * - every response is parsed by a Zod schema and every failure is normalized
 *   to the `ApiError` union
 *
 * Components and hooks call the wrappers below; nothing calls `fetch` on the
 * backend directly.
 */

export interface RequestOptions<T> {
  method?: "GET" | "POST" | "DELETE";
  body?: unknown;
  schema: z.ZodType<T>;
  /**
   * Whether the request carries the owner identity. Everything except
   * `/health` and `/anonymous` does.
   */
  withOwner?: boolean;
  /**
   * Pass a stable key for anything that creates a resource or opens a stream.
   * Retrying the same logical operation must reuse the same key, or the
   * backend will create a duplicate.
   */
  idempotencyKey?: string;
  signal?: AbortSignal;
}

function url(path: string): string {
  return `${env.NEXT_PUBLIC_API_BASE_URL.replace(/\/$/, "")}${path}`;
}

/** A fresh key for one logical operation. Reuse it across retries. */
export function newIdempotencyKey(): string {
  return crypto.randomUUID();
}

async function mintOwnerId(): Promise<string> {
  const response = await fetch(url("/api/v1/anonymous"), { method: "POST" });
  if (!response.ok) {
    throw new ApiErrorException({
      kind: "http",
      status: response.status,
      body: await safeBody(response),
    });
  }
  const parsed = createAnonymousResponseSchema.safeParse(await safeBody(response));
  if (!parsed.success) {
    throw new ApiErrorException({ kind: "parse", issues: parsed.error.issues });
  }
  return parsed.data.owner_id;
}

async function safeBody(response: Response): Promise<unknown> {
  const text = await response.text();
  if (text === "") return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

export async function request<T>(path: string, options: RequestOptions<T>): Promise<T> {
  const { method = "GET", body, schema, withOwner = false, idempotencyKey, signal } = options;

  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (withOwner) headers["X-Anonymous-Owner-Id"] = await getOwnerId(mintOwnerId);
  if (idempotencyKey !== undefined) headers["Idempotency-Key"] = idempotencyKey;

  let response: Response;
  try {
    response = await fetch(url(path), {
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

  const payload = await safeBody(response);

  if (!response.ok) {
    throw new ApiErrorException({ kind: "http", status: response.status, body: payload });
  }

  const parsed = schema.safeParse(payload);
  if (!parsed.success) {
    throw new ApiErrorException({ kind: "parse", issues: parsed.error.issues });
  }

  return parsed.data;
}
