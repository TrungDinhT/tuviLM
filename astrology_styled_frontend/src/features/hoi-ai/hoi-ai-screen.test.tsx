import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ChatMessage, ChatSession, ChatSessionSummary } from "@/lib/api/schemas";
import { OWNER_ID_KEY, resetOwnerIdCache } from "@/lib/api/owner";
import { useChartStore } from "@/store/chart-store";

import { runFixture } from "@/lib/api/runs.test-helpers";

import { HoiAiScreen } from "./hoi-ai-screen";

const toastMocks = vi.hoisted(() => ({ showToast: vi.fn() }));

vi.mock("@/lib/toast", () => toastMocks);

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const SESSIONS: ChatSessionSummary[] = [
  {
    id: "s1",
    chart_profile_id: "p1",
    title: null,
    message_count: 2,
    created_at: "2026-08-29T08:00:00+00:00",
    updated_at: "2026-08-29T08:00:00+00:00",
  },
  {
    id: "s2",
    chart_profile_id: "p1",
    title: null,
    message_count: 1,
    created_at: "2026-08-28T08:00:00+00:00",
    updated_at: "2026-08-28T08:00:00+00:00",
  },
];

function message(over: Partial<ChatMessage>): ChatMessage {
  return {
    id: "m1",
    role: "assistant",
    content: "Xin chào",
    status: "confirmed",
    created_at: "2026-08-29T08:00:00+00:00",
    updated_at: "2026-08-29T08:00:00+00:00",
    ...over,
  };
}

function sessionDetail(id: string, messages: ChatMessage[]): ChatSession {
  return {
    id,
    chart_profile_id: "p1",
    title: null,
    messages,
    created_at: "2026-08-29T08:00:00+00:00",
    updated_at: "2026-08-29T08:00:00+00:00",
  };
}

function setChart(profileId: string | null) {
  useChartStore.setState({
    hasChart: true,
    outcome: null,
    previewOutcome: null,
    chartId: "c1",
    birthInfo: null,
    chartProfileId: profileId,
  });
}

function renderScreen(client: QueryClient) {
  return render(
    <QueryClientProvider client={client}>
      <HoiAiScreen />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  resetOwnerIdCache();
  useChartStore.setState({
    hasChart: false,
    outcome: null,
    previewOutcome: null,
    chartId: null,
    birthInfo: null,
    chartProfileId: null,
  });
});

describe("HoiAiScreen", () => {
  it("renders the re-cast empty state when a chart exists without a profile", () => {
    setChart(null);
    renderScreen(new QueryClient());

    expect(screen.getByText("An sao lại")).toBeTruthy();
  });

  it("opens on the most recent session and renders its transcript", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const fetchMock = vi.fn((url: string) => {
      if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
        return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
      }
      if (url.endsWith("/api/v1/sessions/s1")) {
        return Promise.resolve(
          jsonResponse({
            session: sessionDetail("s1", [
              message({ id: "a1", role: "assistant", content: "Chào bạn, tôi là Thiên Hạc." }),
            ]),
          }),
        );
      }
      if (url.includes("/api/v1/runs?")) return Promise.resolve(jsonResponse([]));
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");

    renderScreen(new QueryClient());

    expect(await screen.findByText("Chào bạn, tôi là Thiên Hạc.")).toBeTruthy();
    // The most recent session is s1; s2 is never opened.
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/v1/sessions/s2"))).toBe(false);
  });

  it("renders a greeting placeholder for an empty session", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
          return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        }
        if (url.endsWith("/api/v1/sessions/s1")) {
          return Promise.resolve(jsonResponse({ session: sessionDetail("s1", []) }));
        }
        if (url.includes("/api/v1/runs?")) return Promise.resolve(jsonResponse([]));
        return Promise.resolve(jsonResponse({}));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());

    expect(await screen.findByText(/tôi là Thiên Hạc/)).toBeTruthy();
  });

  it("switches sessions from the history list", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const fetchMock = vi.fn((url: string) => {
      if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
        return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
      }
      if (url.endsWith("/api/v1/sessions/s1")) {
        return Promise.resolve(
          jsonResponse({ session: sessionDetail("s1", [message({ content: "tin từ s1" })]) }),
        );
      }
      if (url.endsWith("/api/v1/sessions/s2")) {
        return Promise.resolve(
          jsonResponse({ session: sessionDetail("s2", [message({ content: "tin từ s2" })]) }),
        );
      }
      if (url.includes("/api/v1/runs?")) return Promise.resolve(jsonResponse([]));
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");

    renderScreen(new QueryClient());
    expect(await screen.findByText("tin từ s1")).toBeTruthy();

    fireEvent.click(screen.getByText("Lịch sử"));
    fireEvent.click(await screen.findByText(/Cuộc trò chuyện 28\/08/));

    expect(await screen.findByText("tin từ s2")).toBeTruthy();
    await waitFor(() => expect(screen.queryByText("tin từ s1")).toBeNull());
  });

  it("creates a new session from the Tạo mới action", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith("/api/v1/chart-profiles/p1/sessions") && init?.method === "POST") {
        return Promise.resolve(jsonResponse({ session: sessionDetail("s3", []) }));
      }
      if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
        return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
      }
      if (url.endsWith("/api/v1/sessions/s1")) {
        return Promise.resolve(
          jsonResponse({ session: sessionDetail("s1", [message({ content: "tin đã gửi" })]) }),
        );
      }
      if (url.endsWith("/api/v1/sessions/s3")) {
        return Promise.resolve(jsonResponse({ session: sessionDetail("s3", []) }));
      }
      if (url.includes("/api/v1/runs?")) return Promise.resolve(jsonResponse([]));
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("tin đã gửi");

    fireEvent.click(screen.getByText("Tạo mới"));

    await waitFor(() =>
      expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/v1/sessions/s3"))).toBe(true),
    );
  });

  it("disables Tạo mới while the active session has only the greeting", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
          return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        }
        if (url.endsWith("/api/v1/sessions/s1")) {
          return Promise.resolve(jsonResponse({ session: sessionDetail("s1", []) }));
        }
        if (url.includes("/api/v1/runs?")) return Promise.resolve(jsonResponse([]));
        return Promise.resolve(jsonResponse({}));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText(/tôi là Thiên Hạc/);

    const button = screen.getByRole("button", { name: "Tạo mới" });
    expect((button as HTMLButtonElement).disabled).toBe(true);
  });

  it("sends through the shared run API and reconciles saved chat messages", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const running = runFixture({
      workflow: "chat",
      resource_id: "session:s1",
      inputs: { session_id: "s1", content: "Hỏi thử" },
    });
    const finished = runFixture({
      ...running,
      seq: 4,
      status: "succeeded",
      result: { answer: "Câu trả lời" },
      state: {
        text: "Câu trả lời",
        progress: null,
        metadata: { user_message_id: "u2", assistant_message_id: "a2" },
      },
    });
    let saved = false;
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/runs?")) return Promise.resolve(jsonResponse([]));
      if (url.endsWith("/runs") && init?.method === "POST")
        return Promise.resolve(jsonResponse(running));
      if (url.endsWith("/runs/r1")) {
        saved = true;
        return Promise.resolve(jsonResponse(finished));
      }
      if (url.endsWith("/chart-profiles/p1/sessions"))
        return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
      return Promise.resolve(
        jsonResponse({
          session: sessionDetail(
            "s1",
            saved
              ? [
                  message({ id: "u2", role: "user", content: "Hỏi thử" }),
                  message({ id: "a2", content: "Câu trả lời" }),
                ]
              : [],
          ),
        }),
      );
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");
    renderScreen(new QueryClient());
    await screen.findByText(/tôi là Thiên Hạc/);
    await waitFor(() =>
      expect(
        (screen.getByPlaceholderText("Hỏi Thiên Hạc điều gì đó…") as HTMLTextAreaElement).disabled,
      ).toBe(false),
    );
    fireEvent.change(screen.getByPlaceholderText("Hỏi Thiên Hạc điều gì đó…"), {
      target: { value: "Hỏi thử" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Gửi" }));
    await screen.findByText("Câu trả lời", {}, { timeout: 2500 });
    await waitFor(() => expect(screen.getAllByText("Câu trả lời")).toHaveLength(1));
    expect(screen.getAllByText("Hỏi thử")).toHaveLength(1);
    expect(fetchMock.mock.calls.some(([url]) => url.includes("/chat/stream"))).toBe(false);
    expect(
      fetchMock.mock.calls.find(
        ([url, init]) => url.endsWith("/runs") && init?.method === "POST",
      )?.[1]?.body,
    ).toBe(JSON.stringify({ workflow: "chat", inputs: { session_id: "s1", content: "Hỏi thử" } }));
  });

  it("shows a recovered pending workflow and detaches when switching sessions", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const run = runFixture({
      workflow: "chat",
      resource_id: "session:s1",
      inputs: { session_id: "s1", content: "Luận tính cách" },
    });
    let pollSignal: AbortSignal | undefined;
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/runs?"))
        return Promise.resolve(jsonResponse(url.includes("session%3As1") ? [run] : []));
      if (url.endsWith("/runs/r1")) {
        pollSignal = init?.signal ?? undefined;
        return new Promise<Response>((_resolve, reject) => {
          pollSignal?.addEventListener("abort", () => reject(pollSignal?.reason));
        });
      }
      if (url.endsWith("/chart-profiles/p1/sessions"))
        return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
      return Promise.resolve(
        jsonResponse({ session: sessionDetail(url.endsWith("/s2") ? "s2" : "s1", []) }),
      );
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");
    renderScreen(new QueryClient());
    await screen.findByText("Luận tính cách");
    await waitFor(() => expect(pollSignal).toBeDefined(), { timeout: 2500 });
    expect(
      (screen.getByPlaceholderText("Hỏi Thiên Hạc điều gì đó…") as HTMLTextAreaElement).disabled,
    ).toBe(true);
    fireEvent.click(screen.getByText("Lịch sử"));
    fireEvent.click(await screen.findByText(/Cuộc trò chuyện 28\/08/));
    await waitFor(() => expect(pollSignal?.aborted).toBe(true));
    expect(screen.queryByText("Luận tính cách")).toBeNull();
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/cancel"))).toBe(false);
  });

  it("shows a persisted workflow failure with its partial answer", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const run = runFixture({
      workflow: "chat",
      resource_id: "session:s1",
      status: "failed",
      inputs: { session_id: "s1", content: "Hỏi thử" },
      error: "Workflow could not complete",
      state: { text: "Phần trả lời", progress: null, metadata: {} },
    });
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.includes("/runs?")) return Promise.resolve(jsonResponse([run]));
        if (url.endsWith("/chart-profiles/p1/sessions"))
          return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        return Promise.resolve(jsonResponse({ session: sessionDetail("s1", []) }));
      }),
    );
    setChart("p1");
    renderScreen(new QueryClient());
    expect(await screen.findByText("Phần trả lời")).toBeTruthy();
    expect(screen.getByText("Tin nhắn chưa gửi trọn vẹn.")).toBeTruthy();
  });

  it("issues only one create request for repeated activation while pending", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    let resolveCreate: ((response: Response) => void) | undefined;
    const createResponse = new Promise<Response>((resolve) => {
      resolveCreate = resolve;
    });
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith("/api/v1/chart-profiles/p1/sessions") && init?.method === "POST") {
        return createResponse;
      }
      if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
        return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
      }
      if (url.endsWith("/api/v1/sessions/s1")) {
        return Promise.resolve(
          jsonResponse({ session: sessionDetail("s1", [message({ content: "tin đã gửi" })]) }),
        );
      }
      if (url.endsWith("/api/v1/sessions/s3")) {
        return Promise.resolve(jsonResponse({ session: sessionDetail("s3", []) }));
      }
      if (url.includes("/api/v1/runs?")) return Promise.resolve(jsonResponse([]));
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("tin đã gửi");
    const createButton = screen.getByRole("button", { name: "Tạo mới" });
    fireEvent.click(createButton);
    fireEvent.click(createButton);

    await waitFor(() => {
      const createCalls = fetchMock.mock.calls.filter(
        ([url, init]) =>
          url.endsWith("/api/v1/chart-profiles/p1/sessions") && init?.method === "POST",
      );
      expect(createCalls).toHaveLength(1);
    });

    resolveCreate?.(jsonResponse({ session: sessionDetail("s3", []) }));
    await waitFor(() =>
      expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/v1/sessions/s3"))).toBe(true),
    );
  });
});
