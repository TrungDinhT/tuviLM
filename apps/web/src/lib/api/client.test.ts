import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { isApiError } from "@/lib/http/errors";

import fixture from "./__fixtures__/build-laso.json";
import { newIdempotencyKey, request } from "./client";
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

  it("does not send a private request after its account left", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const controller = new AbortController();
    controller.abort();

    await expect(
      request("/api/v1/chart-profiles", {
        method: "POST",
        schema: buildLasoResponseSchema,
        withAuth: true,
        signal: controller.signal,
      }),
    ).rejects.toMatchObject({ name: "AbortError" });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe("headers", () => {
  it("does not call the backend for an account request while signed out", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const error = await errorFrom(
      request("/api/v1/chart-profiles", {
        schema: buildLasoResponseSchema,
        withAuth: true,
        expectedUserId: null,
      }),
    );
    expect(error).toMatchObject({ kind: "http", status: 401 });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("sends idempotency and the expected account but no token: the session cookie goes along by itself", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(fixture));
    vi.stubGlobal("fetch", fetchMock);

    const key = newIdempotencyKey();
    await request("/api/v1/chart-profiles", {
      method: "POST",
      body: {},
      schema: buildLasoResponseSchema,
      withAuth: true,
      expectedUserId: "account-a",
      idempotencyKey: key,
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]![0]).toBe("/api/v1/chart-profiles");
    const headers = fetchMock.mock.calls[0]![1].headers;
    expect(headers["Authorization"]).toBeUndefined();
    expect(headers["Idempotency-Key"]).toBe(key);
    expect(headers["X-Expected-User-Id"]).toBe("account-a");
    expect(headers["Content-Type"]).toBe("application/json");
  });

  it("passes a 401 from the API through without retrying", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ detail: "Authentication required." }, 401));
    vi.stubGlobal("fetch", fetchMock);

    const error = await errorFrom(
      request("/api/v1/chart-profiles", { schema: buildLasoResponseSchema, withAuth: true }),
    );

    expect(error).toMatchObject({ kind: "http", status: 401 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
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
