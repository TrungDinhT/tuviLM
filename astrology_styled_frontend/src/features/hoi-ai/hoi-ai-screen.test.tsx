import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ChatMessage, ChatSession, ChatSessionSummary } from "@/lib/api/schemas";
import { OWNER_ID_KEY, resetOwnerIdCache } from "@/lib/api/owner";
import { useChartStore } from "@/store/chart-store";
import { useToastStore } from "@/store/toast-store";

import { HoiAiScreen } from "./hoi-ai-screen";

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
  localStorage.clear();
  resetOwnerIdCache();
  useToastStore.setState({ message: null });
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
              message({ id: "a1", role: "assistant", content: "Chào bạn, tôi là Nghê Sao." }),
            ]),
          }),
        );
      }
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");

    renderScreen(new QueryClient());

    expect(await screen.findByText("Chào bạn, tôi là Nghê Sao.")).toBeTruthy();
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
        return Promise.resolve(jsonResponse({}));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());

    expect(await screen.findByText(/tôi là Nghê Sao/)).toBeTruthy();
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
        return Promise.resolve(jsonResponse({}));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText(/tôi là Nghê Sao/);

    const button = screen.getByRole("button", { name: "Tạo mới" });
    expect((button as HTMLButtonElement).disabled).toBe(true);
  });

  it("aborts the active stream before switching sessions", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    let streamSignal: AbortSignal | undefined;
    const encoder = new TextEncoder();
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
        return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
      }
      if (url.endsWith("/api/v1/sessions/s1/chat/stream")) {
        streamSignal = init?.signal as AbortSignal | undefined;
        const body = new ReadableStream<Uint8Array>({
          start(controller) {
            controller.enqueue(
              encoder.encode(
                'data: {"type":"ids","user_message_id":"u2","assistant_message_id":"a2"}\n\n',
              ),
            );
            streamSignal?.addEventListener("abort", () => {
              controller.error(new DOMException("Aborted", "AbortError"));
            });
          },
        });
        return Promise.resolve(new Response(body, { status: 200 }));
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
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("tin từ s1");
    fireEvent.change(screen.getByPlaceholderText("Hỏi Nghê Sao điều gì đó…"), {
      target: { value: "Câu hỏi đang chạy" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Gửi" }));
    await waitFor(() => expect(streamSignal).toBeDefined());

    fireEvent.click(screen.getByText("Lịch sử"));
    fireEvent.click(await screen.findByText(/Cuộc trò chuyện 28\/08/));

    expect(streamSignal?.aborted).toBe(true);
    expect(await screen.findByText("tin từ s2")).toBeTruthy();
    expect(screen.queryByText("Câu hỏi đang chạy")).toBeNull();
  });

  it("surfaces a backend error event and preserves partial text", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const stream =
      [
        'data: {"type":"ids","user_message_id":"u2","assistant_message_id":"a2"}',
        'data: {"type":"text","delta":"Phần trả lời"}',
        'data: {"type":"error","message":"internal details"}',
        'data: {"type":"done","status":"failed"}',
      ].join("\n\n") + "\n\n";
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
          return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        }
        if (url.endsWith("/api/v1/sessions/s1/chat/stream")) {
          return Promise.resolve(new Response(stream, { status: 200 }));
        }
        if (url.endsWith("/api/v1/sessions/s1")) {
          return Promise.resolve(
            jsonResponse({ session: sessionDetail("s1", [message({ content: "tin đã gửi" })]) }),
          );
        }
        return Promise.resolve(jsonResponse({}));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("tin đã gửi");
    fireEvent.change(screen.getByPlaceholderText("Hỏi Nghê Sao điều gì đó…"), {
      target: { value: "Hỏi thử" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Gửi" }));

    expect(await screen.findByText("Phần trả lời")).toBeTruthy();
    await waitFor(() =>
      expect(useToastStore.getState().message).toBe(
        "Nghê Sao chưa thể trả lời trọn vẹn. Bạn thử lại nhé.",
      ),
    );
    expect(screen.getByText("Tin nhắn chưa gửi trọn vẹn.")).toBeTruthy();
  });

  it("reconciles a duplicate in-progress stream from the stored assistant message", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    let detailCalls = 0;
    const stream =
      [
        'data: {"type":"duplicate_in_progress","user_message_id":"u2","assistant_message_id":"a2","status":"pending"}',
        'data: {"type":"done","status":"duplicate_in_progress"}',
      ].join("\n\n") + "\n\n";
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
          return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        }
        if (url.endsWith("/api/v1/sessions/s1/chat/stream")) {
          return Promise.resolve(new Response(stream, { status: 200 }));
        }
        if (url.endsWith("/api/v1/sessions/s1")) {
          detailCalls += 1;
          const messages =
            detailCalls === 1
              ? [message({ content: "tin đã gửi" })]
              : [
                  message({ content: "tin đã gửi" }),
                  message({ id: "a2", content: "Câu trả lời đã hoàn tất" }),
                ];
          return Promise.resolve(jsonResponse({ session: sessionDetail("s1", messages) }));
        }
        return Promise.resolve(jsonResponse({}));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("tin đã gửi");
    fireEvent.change(screen.getByPlaceholderText("Hỏi Nghê Sao điều gì đó…"), {
      target: { value: "Hỏi lại cùng key" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Gửi" }));

    expect(await screen.findByText("Câu trả lời đã hoàn tất")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Gửi" }) as HTMLButtonElement).disabled).toBe(false);
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
