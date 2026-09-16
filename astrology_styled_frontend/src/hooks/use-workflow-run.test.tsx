import type { PropsWithChildren } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook as renderQueryHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, expectTypeOf, it, vi } from "vitest";

import { z } from "zod";

import { OWNER_ID_KEY, resetOwnerIdCache } from "@/lib/api/owner";
import { jsonResponse, runFixture } from "@/lib/api/runs.test-helpers";
import { useWorkflowRun } from "./use-workflow-run";

let client: QueryClient;
function wrapper({ children }: PropsWithChildren) {
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
const renderHook: typeof renderQueryHook = (callback, options) =>
  renderQueryHook(callback, { ...options, wrapper });

beforeEach(() => {
  client = new QueryClient();
  localStorage.clear();
  resetOwnerIdCache();
  localStorage.setItem(OWNER_ID_KEY, "owner");
});
afterEach(() => {
  client.clear();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

const options = { workflow: "echo", resourceId: "chart:1" };

describe("useWorkflowRun", () => {
  it("restores a completed run on mount without submitting another workflow", async () => {
    const run = runFixture({ status: "succeeded", result: { answer: "saved" } });
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([run]));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(result.current.run?.result).toEqual({ answer: "saved" }));
    expect(result.current.active).toBe(false);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("restores a running workflow and detaches on unmount without cancellation", async () => {
    const run = runFixture();
    let signal: AbortSignal | undefined;
    const fetchMock = vi.fn((url: string, init: RequestInit) => {
      if (url.includes("/runs?")) return Promise.resolve(jsonResponse([run]));
      signal = init.signal ?? undefined;
      return new Promise<Response>((_resolve, reject) => {
        signal?.addEventListener("abort", () => reject(signal?.reason));
      });
    });
    vi.stubGlobal("fetch", fetchMock);
    const { result, unmount } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(signal).toBeDefined(), { timeout: 2500 });
    expect(result.current.active).toBe(true);
    unmount();
    expect(signal?.aborted).toBe(true);
    expect(fetchMock.mock.calls.every(([url]) => !url.endsWith("/cancel"))).toBe(true);
  });

  it("keeps resource changes isolated from a late response for the previous panel", async () => {
    let completeFirst: (response: Response) => void = () => {};
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.includes("chart%3A1"))
          return new Promise<Response>((resolve) => {
            completeFirst = resolve;
          });
        return Promise.resolve(
          jsonResponse([runFixture({ id: "r2", resource_id: "chart:2", status: "succeeded" })]),
        );
      }),
    );
    const { result, rerender } = renderHook(
      ({ resourceId }) => useWorkflowRun({ workflow: "echo", resourceId }),
      { initialProps: { resourceId: "chart:1" } },
    );
    await act(async () => {
      await Promise.resolve();
    });
    rerender({ resourceId: "chart:2" });
    await waitFor(() => expect(result.current.run?.id).toBe("r2"));
    await act(async () => completeFirst(jsonResponse([runFixture({ status: "succeeded" })])));
    expect(result.current.run?.id).toBe("r2");
  });

  it("reuses a saved submission intent after reopening before the response arrived", async () => {
    const key = `workflow-submit:${JSON.stringify(["owner", "echo", "chart:1"])}`;
    localStorage.setItem(
      key,
      JSON.stringify({ inputs: { question: "Hello" }, key: "original-key" }),
    );
    const run = runFixture({ status: "succeeded", result: "saved" });
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(run));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(result.current.run?.id).toBe("r1"));
    expect(fetchMock.mock.calls[0]?.[1].headers["Idempotency-Key"]).toBe("original-key");
    expect(localStorage.getItem(key)).toBeNull();
  });

  it("submits once for repeated start clicks and applies the final snapshot", async () => {
    const running = runFixture();
    const finished = runFixture({ seq: 3, status: "succeeded", result: "done" });
    const fetchMock = vi.fn((url: string, init: RequestInit) => {
      if (url.includes("/runs?")) return Promise.resolve(jsonResponse([]));
      return Promise.resolve(jsonResponse(init.method === "POST" ? running : finished));
    });
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(result.current.loading).toBe(false));
    act(() => {
      result.current.start({ question: "Hello" });
      result.current.start({ question: "Hello" });
    });
    await waitFor(() => expect(result.current.run?.result).toBe("done"), { timeout: 2500 });
    expect(fetchMock.mock.calls.filter(([, init]) => init.method === "POST")).toHaveLength(1);
  });

  it("uses the cancellation endpoint only for an explicit cancel action", async () => {
    let run = runFixture();
    const fetchMock = vi.fn((url: string) => {
      if (url.includes("/runs?")) return Promise.resolve(jsonResponse([run]));
      if (url.endsWith("/cancel")) {
        run = { ...run, cancel_requested: true };
        return Promise.resolve(jsonResponse(run));
      }
      return Promise.resolve(jsonResponse(run));
    });
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(result.current.active).toBe(true));
    await act(async () => result.current.cancel());
    await waitFor(() => expect(result.current.run?.cancel_requested).toBe(true));
    expect(fetchMock.mock.calls.filter(([url]) => url.endsWith("/cancel"))).toHaveLength(1);
  });

  it("decodes a custom structured output without requiring chat text", async () => {
    const resultSchema = z.object({
      rows: z.array(z.object({ category: z.string(), score: z.number() })),
      recommendations: z.array(z.string()),
    });
    const output = {
      rows: [{ category: "career", score: 0.8 }],
      recommendations: ["Explore options"],
    };
    const run = runFixture({ status: "succeeded", result: output });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse([run])));
    const { result } = renderHook(() => useWorkflowRun({ ...options, resultSchema }));
    await waitFor(() => expect(result.current.result).toEqual(output));
    expect(result.current.run?.state.text).toBe("");
    expectTypeOf(result.current.result).toEqualTypeOf<z.infer<typeof resultSchema> | undefined>();
  });

  it("reports an incompatible result schema without rerunning the workflow", async () => {
    const run = runFixture({ status: "succeeded", result: { answer: "wrong shape" } });
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([run]));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() =>
      useWorkflowRun({ ...options, resultSchema: z.array(z.number()) }),
    );
    await waitFor(() => expect(result.current.error).not.toBeNull());
    expect(result.current.result).toBeUndefined();
    expect(result.current.run?.status).toBe("succeeded");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
  it("retries a lost submission with the same key and saves the result", async () => {
    const finished = runFixture({ status: "succeeded", result: "saved" });
    let posts = 0;
    const fetchMock = vi.fn((url: string, init: RequestInit) => {
      if (url.includes("/runs?")) return Promise.resolve(jsonResponse([]));
      if (init.method === "POST" && ++posts === 1) return Promise.reject(new TypeError("offline"));
      return Promise.resolve(jsonResponse(finished));
    });
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(result.current.loading).toBe(false));
    act(() => result.current.start({ question: "Hello" }));
    await waitFor(() => expect(result.current.result).toBe("saved"), { timeout: 2500 });
    const submissions = fetchMock.mock.calls.filter(([, init]) => init.method === "POST");
    expect(submissions).toHaveLength(2);
    expect(submissions[0][1].headers).toEqual(submissions[1][1].headers);
  });

  it("keeps newer partial text and stops polling after the terminal snapshot", async () => {
    const partial = runFixture({ seq: 4, state: { text: "Part", progress: null, metadata: {} } });
    const finished = runFixture({ seq: 8, status: "succeeded", result: "done" });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([partial]))
      .mockResolvedValueOnce(jsonResponse(runFixture()))
      .mockResolvedValueOnce(jsonResponse(finished));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(result.current.run?.state.text).toBe("Part"));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2), { timeout: 2500 });
    expect(result.current.run?.state.text).toBe("Part");
    await waitFor(() => expect(result.current.result).toBe("done"), { timeout: 2500 });
    await new Promise((resolve) => setTimeout(resolve, 1100));
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("refreshes the saved result when returning to the foreground", async () => {
    const visibility = vi.spyOn(document, "visibilityState", "get").mockReturnValue("hidden");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([runFixture()]))
      .mockResolvedValueOnce(
        jsonResponse(runFixture({ status: "succeeded", seq: 4, result: "done" })),
      );
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(result.current.active).toBe(true));
    act(() => {
      visibility.mockReturnValue("visible");
      document.dispatchEvent(new Event("visibilitychange"));
    });
    await waitFor(() => expect(result.current.result).toBe("done"));
    expect(fetchMock.mock.calls.every(([, init]) => init.method === "GET")).toBe(true);
  });

  it("surfaces permanent HTTP errors without endlessly retrying", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}, 404));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useWorkflowRun(options));
    await waitFor(() => expect(result.current.error).toMatchObject({ error: { status: 404 } }));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
