import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { isApiError } from "@/lib/http/errors";

import fixture from "./__fixtures__/build-laso.json";
import { newIdempotencyKey, request, resolveBaseUrl } from "./client";
import { OWNER_ID_KEY, resetOwnerIdCache } from "./owner";
import { buildLasoResponseSchema } from "./schemas";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

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
  resetOwnerIdCache();
});

afterEach(() => {
  vi.restoreAllMocks();
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

    const error = await errorFrom(
      request("/api/v1/health", { schema: buildLasoResponseSchema }),
    );

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

    await expect(
      request("/api/v1/health", { schema: buildLasoResponseSchema }),
    ).rejects.toBe(abort);
  });
});

describe("headers", () => {
  it("attaches the stored owner id without minting a new one", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(fixture));
    vi.stubGlobal("fetch", fetchMock);

    const key = newIdempotencyKey();
    await request("/api/v1/laso/build", {
      method: "POST",
      body: {},
      schema: buildLasoResponseSchema,
      withOwner: true,
      idempotencyKey: key,
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const headers = fetchMock.mock.calls[0]![1].headers;
    expect(headers["X-Anonymous-Owner-Id"]).toBe("anon_stored");
    expect(headers["Idempotency-Key"]).toBe(key);
    expect(headers["Content-Type"]).toBe("application/json");
  });

  it("omits both headers when they are not requested", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(fixture));
    vi.stubGlobal("fetch", fetchMock);

    await request("/api/v1/laso/build", { schema: buildLasoResponseSchema });

    const headers = fetchMock.mock.calls[0]![1].headers;
    expect(headers["X-Anonymous-Owner-Id"]).toBeUndefined();
    expect(headers["Idempotency-Key"]).toBeUndefined();
  });

  it("mints exactly one owner id when two first requests race", async () => {
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      void init;
      if (url.endsWith("/api/v1/anonymous")) {
        return Promise.resolve(jsonResponse({ owner_id: `anon_${Math.random()}` }));
      }
      return Promise.resolve(jsonResponse(fixture));
    });
    vi.stubGlobal("fetch", fetchMock);

    const [a, b] = await Promise.all([
      request("/api/v1/laso/build", { schema: buildLasoResponseSchema, withOwner: true }),
      request("/api/v1/laso/build", { schema: buildLasoResponseSchema, withOwner: true }),
    ]);

    expect(a).toBeDefined();
    expect(b).toBeDefined();

    const mintCalls = fetchMock.mock.calls.filter(([url]) =>
      String(url).endsWith("/api/v1/anonymous"),
    );
    expect(mintCalls).toHaveLength(1);

    const sent = fetchMock.mock.calls
      .filter(([url]) => url.endsWith("/api/v1/laso/build"))
      .map(([, init]) => (init?.headers as Record<string, string>)["X-Anonymous-Owner-Id"]);
    expect(new Set(sent).size).toBe(1);
    expect(localStorage.getItem(OWNER_ID_KEY)).toBe(sent[0]);
  });

  it("does not poison later attempts when minting fails", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ detail: "boom" }, 500))
      .mockResolvedValueOnce(jsonResponse({ owner_id: "anon_second" }))
      .mockResolvedValue(jsonResponse(fixture));
    vi.stubGlobal("fetch", fetchMock);

    await errorFrom(
      request("/api/v1/laso/build", { schema: buildLasoResponseSchema, withOwner: true }),
    );

    await request("/api/v1/laso/build", { schema: buildLasoResponseSchema, withOwner: true });

    expect(localStorage.getItem(OWNER_ID_KEY)).toBe("anon_second");
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
