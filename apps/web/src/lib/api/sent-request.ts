/**
 * Test helper: one `fetch` call as the Effect HTTP client made it, in a shape
 * a test can assert on. The client passes a `URL`, lower-cased headers and a
 * byte body; this reads them back as a path, a `Headers` and parsed JSON.
 */
export interface SentRequest {
  url: string;
  path: string;
  method: string;
  headers: Headers;
  body: unknown;
  signal: AbortSignal | null | undefined;
  cache: RequestCache | undefined;
}

export const sentRequest = (call: readonly unknown[] | undefined): SentRequest => {
  const [input, init = {}] = (call ?? []) as [RequestInfo | URL, RequestInit | undefined];
  const url = input instanceof Request ? input.url : String(input);
  const raw = init.body;
  const text =
    raw === undefined || raw === null
      ? undefined
      : typeof raw === "string"
        ? raw
        : new TextDecoder().decode(raw as Uint8Array);
  return {
    url,
    path: new URL(url, "http://localhost").pathname,
    method: init.method ?? "GET",
    headers: new Headers(init.headers),
    body: text === undefined ? undefined : (JSON.parse(text) as unknown),
    signal: init.signal,
    cache: init.cache,
  };
};

/** Every call of a `fetch` mock, as sent requests. */
export const sentRequests = (mock: { mock: { calls: readonly (readonly unknown[])[] } }) =>
  mock.mock.calls.map(sentRequest);
