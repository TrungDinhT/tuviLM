import { Cause, Effect, Exit, Result, type Schema } from "effect";
import {
  FetchHttpClient,
  HttpClient,
  HttpClientRequest,
  type HttpClientError,
  type HttpClientResponse,
} from "effect/http";

import { ApiErrorException } from "@/lib/http/errors";
import { validate } from "@/lib/schema";

/**
 * The only place in the application that talks to the FastAPI backend.
 *
 * Three things happen here and nowhere else:
 * - requests go to same-origin `/api` paths, which Next forwards to FastAPI
 * - idempotency headers are attached (the session cookie goes along by itself)
 * - every response is decoded by an Effect schema and every failure is
 *   normalized to the `ApiError` union
 *
 * Requests are Effect programs that need an `HttpClient` and fail with
 * `ApiErrorException`. `runApi` runs one as a promise for TanStack Query;
 * nothing calls `fetch` on the backend directly.
 */

export type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

export interface RequestOptions<T> {
  method?: HttpMethod;
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

/** A body as JSON when it is JSON, as text when it is not, `null` when empty. */
export const parseBody = (text: string): unknown => {
  if (text === "") return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
};

/**
 * The account this page was loaded for. The API refuses the request if the
 * session cookie belongs to someone else, e.g. after a sign-in in another tab.
 */
export const expectedUserHeader = (
  expectedUserId: string | null | undefined,
): Record<string, string> => (expectedUserId ? { "X-Expected-User-Id": expectedUserId } : {});

/** An account request made while signed out fails without a round trip. */
export const ensureSignedIn = (
  expectedUserId: string | null | undefined,
): Effect.Effect<void, ApiErrorException> =>
  expectedUserId === null
    ? Effect.fail(
        new ApiErrorException({
          kind: "http",
          status: 401,
          body: { detail: "Authentication required" },
        }),
      )
    : Effect.void;

const isAbort = (cause: unknown): cause is DOMException =>
  cause instanceof DOMException && cause.name === "AbortError";

/**
 * A transport failure is a `network` error, except an abort: that is the
 * caller's own doing, so it stays an abort (a defect here, rethrown as is).
 */
export const fromTransport =
  (error: ApiErrorException) =>
  (failure: HttpClientError.HttpClientError): Effect.Effect<never, ApiErrorException> =>
    isAbort(failure.reason.cause) ? Effect.die(failure.reason.cause) : Effect.fail(error);

/** Send one request. Only an abort escapes as something other than `ApiErrorException`. */
export const send = (
  request: HttpClientRequest.HttpClientRequest,
): Effect.Effect<HttpClientResponse.HttpClientResponse, ApiErrorException, HttpClient.HttpClient> =>
  HttpClient.HttpClient.pipe(
    Effect.flatMap((client) => client.execute(request)),
    Effect.catchTag("HttpClientError", fromTransport(new ApiErrorException({ kind: "network" }))),
  );

/** The response body, decoded by `parseBody`. */
export const readBody = (
  response: HttpClientResponse.HttpClientResponse,
): Effect.Effect<unknown, ApiErrorException> =>
  response.text.pipe(
    Effect.map(parseBody),
    Effect.catchTag("HttpClientError", fromTransport(new ApiErrorException({ kind: "network" }))),
  );

const isOk = (response: HttpClientResponse.HttpClientResponse) =>
  response.status >= 200 && response.status < 300;

/** A non-2xx response as an `http` error carrying its status and body. */
export const failOnHttpError = (
  response: HttpClientResponse.HttpClientResponse,
): Effect.Effect<HttpClientResponse.HttpClientResponse, ApiErrorException> =>
  isOk(response)
    ? Effect.succeed(response)
    : readBody(response).pipe(
        Effect.flatMap((body) =>
          Effect.fail(new ApiErrorException({ kind: "http", status: response.status, body })),
        ),
      );

/** Decode `payload`, or fail with a `parse` error that carries every issue. */
export const decodePayload = <T>(
  schema: Schema.ConstraintDecoder<T>,
  payload: unknown,
): Effect.Effect<T, ApiErrorException> =>
  Result.match(validate(schema, payload), {
    onSuccess: (value) => Effect.succeed(value),
    onFailure: (issues) => Effect.fail(new ApiErrorException({ kind: "parse", issues })),
  });

/** The request headers: the expected account and the idempotency key. */
export const apiHeaders = (options: {
  expectedUserId?: string | null;
  idempotencyKey?: string;
}): Record<string, string> => ({
  ...(options.idempotencyKey === undefined ? {} : { "Idempotency-Key": options.idempotencyKey }),
  ...expectedUserHeader(options.expectedUserId),
});

/** Build the request for `path`, with a JSON body when one is given. */
export const makeRequest = (
  path: string,
  options: { method?: HttpMethod; body?: unknown } & Parameters<typeof apiHeaders>[0],
): HttpClientRequest.HttpClientRequest => {
  const request = HttpClientRequest.make(options.method ?? "GET")(path, {
    headers: apiHeaders(options),
  });
  return options.body === undefined
    ? request
    : HttpClientRequest.bodyJsonUnsafe(request, options.body);
};

/** One API call as an Effect: send, check the status, decode the body. */
export const apiRequest = <T>(
  path: string,
  options: RequestOptions<T>,
): Effect.Effect<T, ApiErrorException, HttpClient.HttpClient> =>
  Effect.gen(function* () {
    if (options.withAuth) yield* ensureSignedIn(options.expectedUserId);
    const response = yield* send(makeRequest(path, options)).pipe(Effect.flatMap(failOnHttpError));
    const payload = yield* readBody(response);
    return yield* decodePayload(options.schema, payload);
  });

/**
 * The browser `fetch`, read at call time rather than captured once, so a
 * polyfill or a test stub installed later still applies.
 */
const lateFetch: typeof globalThis.fetch = (input, init) => globalThis.fetch(input, init);

/**
 * Provide the fetch-based `HttpClient`. Trace propagation is off: the API
 * does not read `traceparent`, and the headers would only add noise.
 */
export const provideHttpClient = <A, E>(
  effect: Effect.Effect<A, E, HttpClient.HttpClient>,
): Effect.Effect<A, E> =>
  effect.pipe(
    Effect.provide(FetchHttpClient.layer),
    Effect.provideService(FetchHttpClient.Fetch, lateFetch),
    Effect.provideService(HttpClient.TracerPropagationEnabled, false),
  );

/**
 * Run an API effect as a promise. An abort of `signal` interrupts it and
 * rejects with the signal's reason (an `AbortError`); any other failure
 * rejects with the error itself, usually an `ApiErrorException`.
 */
export const runApi = async <A>(
  effect: Effect.Effect<A, ApiErrorException, HttpClient.HttpClient>,
  signal?: AbortSignal,
): Promise<A> => {
  signal?.throwIfAborted();
  const exit = await Effect.runPromiseExit(provideHttpClient(effect), { signal });
  signal?.throwIfAborted();
  if (Exit.isSuccess(exit)) return exit.value;
  throw Cause.squash(exit.cause);
};

/** One API call as a promise, for TanStack Query. */
export const request = <T>(
  path: string,
  { signal, ...options }: RequestOptions<T> & { signal?: AbortSignal },
): Promise<T> => runApi(apiRequest(path, options), signal);
