import { ApiErrorException } from "@/lib/http/errors";

import { apiUrl, mintOwnerId, safeBody } from "./client";
import { getOwnerId } from "./owner";
import { sseChatEventSchema, type SseChatEvent } from "./schemas";

/**
 * The SSE reader for chat.
 *
 * Streams are not TanStack Query queries, so they do not go through `request`
 * (which reads the whole body). They do, however, share the client's rules:
 * the same base-URL/host resolution (`apiUrl`), the same identity and
 * idempotency headers, and the same normalized `ApiError` failures.
 *
 * The backend sends one `data: {…}\n\n` frame per event. A frame is split
 * into `data:` lines and JSON-decoded; an event that fails the Zod schema
 * resolves to the `stream` error variant rather than corrupting the transcript.
 */

/**
 * Stream a chat turn from the backend, yielding typed SSE events.
 *
 * The caller owns `idempotencyKey` so retrying this logical turn can reuse it.
 * The generator throws `ApiErrorException` for network, HTTP, and parse
 * failures; the backend's own `error` event arrives as a yielded `error`
 * event, followed by a `done` event carrying the failed status.
 */
export async function* streamChat(
  sessionId: string,
  content: string,
  opts: { idempotencyKey: string; signal?: AbortSignal },
): AsyncGenerator<SseChatEvent> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Anonymous-Owner-Id": await getOwnerId(mintOwnerId),
    "Idempotency-Key": opts.idempotencyKey,
  };

  let response: Response;
  try {
    response = await fetch(apiUrl(`/api/v1/sessions/${sessionId}/chat/stream`), {
      method: "POST",
      headers,
      body: JSON.stringify({ content }),
      signal: opts.signal,
    });
  } catch (cause) {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    throw new ApiErrorException({ kind: "network" });
  }

  if (!response.ok) {
    throw new ApiErrorException({
      kind: "http",
      status: response.status,
      body: await safeBody(response),
    });
  }

  if (response.body === null) {
    throw new ApiErrorException({ kind: "stream", event: "empty body" });
  }

  yield* parseSseStream(response.body);
}

/**
 * Parse a `ReadableStream` of SSE frames into typed chat events.
 *
 * Buffers partial frames across chunk boundaries and partial UTF-8 sequences
 * across `decoder` calls. A frame without a `data:` line is ignored (a
 * heartbeat or comment); a frame whose data fails the schema throws the
 * `stream` error carrying the raw frame.
 */
export async function* parseSseStream(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<SseChatEvent> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary: number;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const rawFrame = buffer.slice(0, boundary).replace(/\r/g, "");
      buffer = buffer.slice(boundary + 2);

      const data = extractData(rawFrame);
      if (data === null) continue;

      const parsed = sseChatEventSchema.safeParse(data);
      if (!parsed.success) {
        throw new ApiErrorException({ kind: "stream", event: rawFrame });
      }
      yield parsed.data;
    }
  }
}

/** Join the `data:` lines of one SSE frame and JSON-decode them. */
function extractData(rawFrame: string): unknown | null {
  const dataLines = rawFrame
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trimStart());

  if (dataLines.length === 0) return null;

  const joined = dataLines.join("\n");
  try {
    return JSON.parse(joined) as unknown;
  } catch {
    // Not JSON — return the string so the schema rejects it as a `stream`
    // error rather than silently dropping the frame.
    return joined;
  }
}
