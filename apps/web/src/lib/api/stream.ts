import { Effect, Option, Schema, Stream } from "effect";
import type { HttpClient } from "effect/http";

import { ApiErrorException } from "@/lib/http/errors";

import { ensureSignedIn, failOnHttpError, fromTransport, makeRequest, send } from "./client";
import { apiEndpoints } from "./endpoints";
import { sseChatEventSchema, type SseChatEvent } from "./schemas";

/**
 * The SSE reader for chat.
 *
 * Streams are not TanStack Query queries, so they do not go through
 * `apiRequest` (which reads the whole body). They do, however, share the
 * client's rules: same-origin `/api` paths, the same identity and idempotency
 * headers, and the same normalized `ApiError` failures.
 *
 * The backend sends one `data: {…}\n\n` frame per event. A frame is split
 * into `data:` lines and JSON-decoded; an event that fails the schema fails
 * the stream with the `stream` error variant rather than corrupting the
 * transcript.
 */

/** The body broke off mid-turn. */
const connectionLost = () => new ApiErrorException({ kind: "stream", event: "connection lost" });

/**
 * Stream a chat turn from the backend as typed SSE events.
 *
 * The caller owns `idempotencyKey` so retrying this logical turn can reuse it.
 * The stream fails with `ApiErrorException` for network, HTTP, and parse
 * failures; the backend's own `error` event arrives as an `error` event,
 * followed by a `done` event carrying the failed status. Run it with
 * `runApi` and the turn's abort signal.
 */
export const chatEvents = (
  sessionId: string,
  content: string,
  opts: { idempotencyKey: string; expectedUserId?: string | null },
): Stream.Stream<SseChatEvent, ApiErrorException, HttpClient.HttpClient> =>
  Stream.unwrap(
    Effect.gen(function* () {
      yield* ensureSignedIn(opts.expectedUserId);
      const response = yield* send(
        makeRequest(apiEndpoints.chatStream(sessionId), {
          method: "POST",
          body: { content },
          idempotencyKey: opts.idempotencyKey,
          expectedUserId: opts.expectedUserId,
        }),
      ).pipe(Effect.flatMap(failOnHttpError));
      return sseEvents(
        response.stream.pipe(
          Stream.catchTag("HttpClientError", (failure) =>
            Stream.fromEffect(fromTransport(connectionLost())(failure)),
          ),
        ),
      );
    }),
  );

/**
 * Parse a byte stream of SSE frames into typed chat events.
 *
 * Text decoding keeps a UTF-8 sequence split across chunks intact, and a
 * frame split across chunks is buffered until its blank line arrives. A frame
 * without a `data:` line is ignored (a heartbeat or comment); a frame whose
 * data fails the schema fails the stream with the `stream` error carrying the
 * raw frame.
 */
export const sseEvents = <E, R>(
  bytes: Stream.Stream<Uint8Array, E, R>,
): Stream.Stream<SseChatEvent, E | ApiErrorException, R> =>
  bytes.pipe(
    Stream.decodeText(),
    Stream.mapAccum(
      () => "",
      (buffer, chunk): readonly [string, ReadonlyArray<string>] => {
        const frames = (buffer + chunk).split("\n\n");
        const rest = frames.pop() ?? "";
        return [rest, frames.map((frame) => frame.replace(/\r/g, ""))];
      },
    ),
    Stream.mapEffect(decodeFrame),
    Stream.flattenIterable,
  );

const decodeEvent = Schema.decodeUnknownOption(sseChatEventSchema);

/** The events of one frame: one, or none for a frame without data. */
const decodeFrame = (
  rawFrame: string,
): Effect.Effect<ReadonlyArray<SseChatEvent>, ApiErrorException> =>
  Option.match(extractData(rawFrame), {
    onNone: () => Effect.succeed([]),
    onSome: (data) =>
      Option.match(decodeEvent(data), {
        onNone: () => Effect.fail(new ApiErrorException({ kind: "stream", event: rawFrame })),
        onSome: (event) => Effect.succeed([event]),
      }),
  });

/** Join the `data:` lines of one SSE frame and JSON-decode them. */
const extractData = (rawFrame: string): Option.Option<unknown> => {
  const dataLines = rawFrame
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trimStart());

  if (dataLines.length === 0) return Option.none();

  const joined = dataLines.join("\n");
  try {
    return Option.some(JSON.parse(joined) as unknown);
  } catch {
    // Not JSON — keep the string so the schema rejects it as a `stream`
    // error rather than silently dropping the frame.
    return Option.some(joined);
  }
};
