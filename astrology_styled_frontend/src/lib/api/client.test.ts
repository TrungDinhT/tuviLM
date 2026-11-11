import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { isApiError } from "@/lib/http/errors";
import { authClient } from "@/lib/auth-client";

import fixture from "./__fixtures__/build-laso.json";
import { clearAuthToken } from "./auth-headers";
import { newIdempotencyKey, request, resolveBaseUrl } from "./client";
import { OWNER_ID_KEY } from "./owner";
import { buildLasoResponseSchema } from "./schemas";

vi.mock("@/lib/auth-client", () => ({ authClient: { token: vi.fn() } }));

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function signedToken(claims: Record<string, unknown>) {
  const payload = btoa(JSON.stringify(claims))
    .replace(/=+$/, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
  return `header.${payload}.signature`;
}

const inAnHour = () => Math.floor(Date.now() / 1000) + 3600;

/** Unwrap the ApiError the client threw, failing the test if it threw anything else. */
async function errorFrom(promise: Promise<unknown>) {
  try {
    await promise;
  } catch (caught) {
    if (isApiError(caught)) return caught.error;
    throw caught;
  }
  throw new Error("expected the request to reject");
}

beforeEach(() => {
  localStorage.clear();
  clearAuthToken();
  vi.mocked(authClient.token).mockReset();
  vi.mocked(authClient.token).mockResolvedValue({ data: { token: "signed-token" }, error: null });
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("request", () => {
  it("parses a real backend response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(fixture)));

    const result = await request("/api/v1/laso/build", {
      method: "POST",
      body: { calendar: "solar", year: 2009, month: 4, day: 4, hour: 5, gender: "M" },
      schema: buildLasoResponseSchema,
    });

    expect(Object.keys(result.cung_by_position)).toHaveLength(12);
    expect(result.ban_menh_name).toBe("Tích Lịch Hỏa");
  });

  it("reports schema drift as a parse error carrying the issues", async () => {
    const drifted = { ...fixture, cung_by_position: { Tý: { position: 1 } } };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(drifted)));

    const error = await errorFrom(
      request("/api/v1/laso/build", { method: "POST", schema: buildLasoResponseSchema }),
    );

    expect(error.kind).toBe("parse");
    if (error.kind === "parse") expect(error.issues.length).toBeGreaterThan(0);
  });

  it("reports an unreachable backend as a network error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const error = await errorFrom(request("/api/v1/health", { schema: buildLasoResponseSchema }));

    expect(error).toEqual({ kind: "network" });
  });

  it("preserves status and body on an HTTP error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ detail: "day is out of range for month" }, 422)),
    );

    const error = await errorFrom(
      request("/api/v1/laso/build", { method: "POST", schema: buildLasoResponseSchema }),
    );

    expect(error).toEqual({
      kind: "http",
      status: 422,
      body: { detail: "day is out of range for month" },
    });
  });

  it("lets an abort propagate rather than disguising it as a network failure", async () => {
    const abort = new DOMException("The operation was aborted.", "AbortError");
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(abort));

    await expect(request("/api/v1/health", { schema: buildLasoResponseSchema })).rejects.toBe(
      abort,
    );
  });

  it("does not send a private request if the account leaves while its token loads", async () => {
    let resolveToken!: (value: { data: { token: string }; error: null }) => void;
    vi.mocked(authClient.token).mockReturnValue(
      new Promise((resolve) => {
        resolveToken = resolve;
      }),
    );
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const controller = new AbortController();
    const pending = request("/api/v1/chart-profiles", {
      method: "POST",
      schema: buildLasoResponseSchema,
      withAuth: true,
      signal: controller.signal,
    });
    const rejected = expect(pending).rejects.toMatchObject({ name: "AbortError" });
    controller.abort();
    resolveToken({ data: { token: "new-account-token" }, error: null });
    await rejected;
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe("headers", () => {
  it("does not send data for account A using account B's token", async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: "header.eyJzdWIiOiJhY2NvdW50LWIifQ.signature" },
      error: null,
    });
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const error = await errorFrom(
      request("/api/v1/chart-profiles", {
        method: "POST",
        body: { birth_info: "account-a-input" },
        schema: buildLasoResponseSchema,
        withAuth: true,
        expectedUserId: "account-a",
      }),
    );
    expect(error).toMatchObject({ kind: "http", status: 401 });
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it("attaches bearer identity and idempotency without minting an anonymous owner", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(fixture));
    vi.stubGlobal("fetch", fetchMock);

    const key = newIdempotencyKey();
    await request("/api/v1/chart-profiles", {
      method: "POST",
      body: {},
      schema: buildLasoResponseSchema,
      withAuth: true,
      idempotencyKey: key,
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const headers = fetchMock.mock.calls[0]![1].headers;
    expect(headers["Authorization"]).toBe("Bearer signed-token");
    expect(headers["X-Anonymous-Owner-Id"]).toBeUndefined();
    expect(headers["Idempotency-Key"]).toBe(key);
    expect(headers["Content-Type"]).toBe("application/json");
  });

  it("does not acquire identity for a public request", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(fixture));
    vi.stubGlobal("fetch", fetchMock);

    await request("/api/v1/laso/build", { schema: buildLasoResponseSchema });

    const headers = fetchMock.mock.calls[0]![1].headers;
    expect(headers["X-Anonymous-Owner-Id"]).toBeUndefined();
    expect(headers["Authorization"]).toBeUndefined();
    expect(headers["Idempotency-Key"]).toBeUndefined();
    expect(authClient.token).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("reuses an unexpired token for the same account", async () => {
    const token = signedToken({ sub: "account-a", exp: inAnHour() });
    vi.mocked(authClient.token).mockResolvedValue({ data: { token }, error: null });
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(fixture)));
    vi.stubGlobal("fetch", fetchMock);
    const options = {
      schema: buildLasoResponseSchema,
      withAuth: true,
      expectedUserId: "account-a",
    };

    await Promise.all([
      request("/api/v1/chart-profiles", options),
      request("/api/v1/chart-profiles", options),
    ]);
    await request("/api/v1/chart-profiles", options);

    expect(authClient.token).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls.map(([, init]) => init.headers.Authorization)).toEqual(
      Array(3).fill(`Bearer ${token}`),
    );
    expect(localStorage.length).toBe(0);
  });

  it("does not reuse a token that is about to expire or belongs to another account", async () => {
    const expiring = signedToken({ sub: "account-a", exp: Math.floor(Date.now() / 1000) + 30 });
    const accountA = signedToken({ sub: "account-a", exp: inAnHour() });
    const accountB = signedToken({ sub: "account-b", exp: inAnHour() });
    vi.mocked(authClient.token)
      .mockResolvedValueOnce({ data: { token: expiring }, error: null })
      .mockResolvedValueOnce({ data: { token: accountA }, error: null })
      .mockResolvedValueOnce({ data: { token: accountB }, error: null });
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(fixture)));
    vi.stubGlobal("fetch", fetchMock);

    for (const expectedUserId of ["account-a", "account-a", "account-b"]) {
      await request("/api/v1/chart-profiles", {
        schema: buildLasoResponseSchema,
        withAuth: true,
        expectedUserId,
      });
    }

    expect(fetchMock.mock.calls.map(([, init]) => init.headers.Authorization)).toEqual([
      `Bearer ${expiring}`,
      `Bearer ${accountA}`,
      `Bearer ${accountB}`,
    ]);
  });

  it("retries once with a new token when the API rejects a cached one", async () => {
    const revoked = signedToken({ sub: "account-a", exp: inAnHour(), sid: "revoked" });
    const current = signedToken({ sub: "account-a", exp: inAnHour(), sid: "current" });
    vi.mocked(authClient.token)
      .mockResolvedValueOnce({ data: { token: revoked }, error: null })
      .mockResolvedValueOnce({ data: { token: current }, error: null });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(fixture))
      .mockResolvedValueOnce(jsonResponse({ detail: "Session expired." }, 401))
      .mockResolvedValueOnce(jsonResponse(fixture));
    vi.stubGlobal("fetch", fetchMock);
    const options = {
      schema: buildLasoResponseSchema,
      withAuth: true,
      expectedUserId: "account-a",
    };

    await request("/api/v1/chart-profiles", options);
    await request("/api/v1/chart-profiles", options);

    expect(fetchMock.mock.calls.map(([, init]) => init.headers.Authorization)).toEqual([
      `Bearer ${revoked}`,
      `Bearer ${revoked}`,
      `Bearer ${current}`,
    ]);
  });

  it("does not call the backend when authentication fails or poison later attempts", async () => {
    vi.mocked(authClient.token)
      .mockResolvedValueOnce({ data: { token: "" }, error: null })
      .mockResolvedValueOnce({ data: { token: "signed-token" }, error: null });
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(fixture));
    vi.stubGlobal("fetch", fetchMock);

    const error = await errorFrom(
      request("/api/v1/chart-profiles", { schema: buildLasoResponseSchema, withAuth: true }),
    );
    expect(error).toMatchObject({ kind: "http", status: 401 });
    expect(fetchMock).not.toHaveBeenCalled();

    await request("/api/v1/chart-profiles", { schema: buildLasoResponseSchema, withAuth: true });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe("resolveBaseUrl", () => {
  it("leaves the configured URL alone on the server", () => {
    expect(resolveBaseUrl("http://localhost:8000", null)).toBe("http://localhost:8000");
  });

  it("leaves it alone when the page is on the same host", () => {
    expect(resolveBaseUrl("http://localhost:8000", "localhost")).toBe("http://localhost:8000");
  });

  // Dev on a phone: the page came from the LAN, so localhost would be the phone.
  it("borrows the page host when the base points at localhost", () => {
    expect(resolveBaseUrl("http://localhost:8000", "192.168.1.23")).toBe(
      "http://192.168.1.23:8000",
    );
    expect(resolveBaseUrl("http://127.0.0.1:8000/", "192.168.1.23")).toBe(
      "http://192.168.1.23:8000",
    );
  });

  it("never rewrites a real backend URL", () => {
    expect(resolveBaseUrl("https://api.tuvi.example", "192.168.1.23")).toBe(
      "https://api.tuvi.example",
    );
  });
});

describe("newIdempotencyKey", () => {
  it("returns a non-empty key", () => {
    expect(newIdempotencyKey().length).toBeGreaterThan(0);
  });

  it("falls back when crypto.randomUUID is unavailable (plain HTTP over LAN)", () => {
    const original = globalThis.crypto;
    vi.stubGlobal("crypto", { getRandomValues: () => undefined, randomUUID: undefined });
    try {
      const key = newIdempotencyKey();
      expect(key.startsWith("id-")).toBe(true);
      expect(key.length).toBeGreaterThan(3);
    } finally {
      vi.stubGlobal("crypto", original);
    }
  });
});
