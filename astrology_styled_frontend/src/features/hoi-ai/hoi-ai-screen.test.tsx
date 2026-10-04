import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { BalanceBadge } from "@/components/shell/balance-badge";
import { AccountRequestContext } from "@/lib/api/account-request";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  AccountAccess,
  ChatMessage,
  ChatSession,
  ChatSessionSummary,
} from "@/lib/api/schemas";
import { useChartStore } from "@/store/chart-store";

import { HoiAiScreen } from "./hoi-ai-screen";

const toastMocks = vi.hoisted(() => ({ showToast: vi.fn() }));
const accountState = vi.hoisted(() => ({
  data: { user: { id: "user-1", name: "Test User" } } as {
    user: { id: string; name: string };
  } | null,
  isPending: false,
}));

vi.mock("@/lib/toast", () => toastMocks);

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    useSession: () => accountState,
    token: vi.fn().mockResolvedValue({
      data: { token: "header.eyJzdWIiOiJ1c2VyLTEifQ.signature" },
      error: null,
    }),
  },
}));

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

const ACCESS: AccountAccess = { user_id: "user-1", role: "user", plan: "normal", balance: 6 };

function renderScreen(client: QueryClient, loadAccess = false) {
  const userId = accountState.data?.user.id ?? null;
  if (!loadAccess && userId !== null) {
    client.setQueryDefaults(queryKeys.accountAccess(userId), { refetchOnMount: false });
    client.setQueryData(queryKeys.accountAccess(userId), ACCESS);
  }
  return render(
    <QueryClientProvider client={client}>
      <AccountRequestContext.Provider value={{ getSignal: () => undefined, userId }}>
        <header>
          <BalanceBadge />
        </header>
        <HoiAiScreen />
      </AccountRequestContext.Provider>
    </QueryClientProvider>,
  );
}

function mockBillingChat(stream: string | ReadableStream<Uint8Array>, access: () => AccountAccess) {
  const fetchMock = vi.fn((url: string) => {
    if (url.endsWith("/api/v1/me")) return Promise.resolve(jsonResponse(access()));
    if (url.endsWith("/chat/stream")) return Promise.resolve(new Response(stream, { status: 200 }));
    if (url.endsWith("/sessions")) return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
    return Promise.resolve(
      jsonResponse({ session: sessionDetail("s1", [message({ content: "Previous reply" })]) }),
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  setChart("p1");
  return fetchMock;
}

async function sendQuestion() {
  await screen.findByText("Previous reply");
  const input = screen.getByRole("textbox");
  fireEvent.change(input, { target: { value: "My question" } });
  fireEvent.keyDown(input, { key: "Enter" });
}

beforeEach(() => {
  vi.clearAllMocks();
  accountState.data = { user: { id: "user-1", name: "Test User" } };
  localStorage.clear();
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
  it("shows Full unlock without exposing its coin balance", async () => {
    mockBillingChat("", () => ({ ...ACCESS, plan: "full_unlock", balance: 1234 }));
    renderScreen(new QueryClient(), true);
    expect(await screen.findByText("Chat AI đã được bao gồm trong gói Full unlock.")).toBeTruthy();
    expect(screen.getByText("Full unlock")).toBeTruthy();
    expect(screen.queryByText(/coins|1,234|1234/i)).toBeNull();
    expect(screen.queryByLabelText("Account balance")).toBeNull();
    expect(screen.getByLabelText("Full unlock").getAttribute("title") ?? "").not.toMatch(
      /coins|1,234|1234/i,
    );
    await screen.findByText("Previous reply");
    expect((screen.getByRole("textbox") as HTMLInputElement).disabled).toBe(false);
  });

  it("keeps the displayed balance until a successful reply refreshes it from the server", async () => {
    let finish!: () => void;
    const encoder = new TextEncoder();
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(
          encoder.encode(
            'data: {"type":"ids","user_message_id":"u2","assistant_message_id":"a2"}\n\ndata: {"type":"text","delta":"Working reply"}\n\n',
          ),
        );
        finish = () => {
          controller.enqueue(encoder.encode('data: {"type":"done","status":"confirmed"}\n\n'));
          controller.close();
        };
      },
    });
    let reads = 0;
    mockBillingChat(stream, () => ({ ...ACCESS, balance: ++reads === 1 ? 6 : 3 }));
    renderScreen(new QueryClient(), true);
    await screen.findByText("6 coins");
    expect(
      screen.getByText("Chat AI: 3 coins mỗi tin nhắn. Chỉ trừ coins khi AI trả lời hoàn tất."),
    ).toBeTruthy();
    await sendQuestion();
    await screen.findByText("Working reply");
    expect(screen.getByText("6 coins")).toBeTruthy();
    expect(reads).toBe(1);
    finish();
    expect(await screen.findByText("3 coins")).toBeTruthy();
    expect(reads).toBe(2);
  });

  it("refreshes the server balance after a failed reply without charging locally", async () => {
    let reads = 0;
    const stream =
      'data: {"type":"error","message":"AI unavailable"}\n\ndata: {"type":"done","status":"failed"}\n\n';
    mockBillingChat(stream, () => {
      reads += 1;
      return ACCESS;
    });
    renderScreen(new QueryClient(), true);
    await screen.findByText("6 coins");
    await sendQuestion();
    await waitFor(() => expect(reads).toBe(2));
    expect(screen.getByText("6 coins")).toBeTruthy();
    expect((screen.getByRole("textbox") as HTMLInputElement).disabled).toBe(false);
  });

  it("asks guests to sign in without fetching private sessions", () => {
    accountState.data = null;
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    setChart("legacy-profile");

    renderScreen(new QueryClient());

    expect(screen.getByText("Sign in to save your chart and use AI chat.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Sign in" }).getAttribute("href")).toBe("/login");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("renders the re-cast empty state when a chart exists without a profile", () => {
    setChart(null);
    renderScreen(new QueryClient());

    expect(screen.getByText("An sao lại")).toBeTruthy();
  });

  it("opens on the most recent session and renders its transcript", async () => {
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
      return Promise.resolve(jsonResponse(ACCESS));
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");

    renderScreen(new QueryClient());

    expect(await screen.findByText("Chào bạn, tôi là Thiên Hạc.")).toBeTruthy();
    // The most recent session is s1; s2 is never opened.
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/api/v1/sessions/s2"))).toBe(false);
  });

  it("renders a greeting placeholder for an empty session", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
          return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        }
        if (url.endsWith("/api/v1/sessions/s1")) {
          return Promise.resolve(jsonResponse({ session: sessionDetail("s1", []) }));
        }
        return Promise.resolve(jsonResponse(ACCESS));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());

    expect(await screen.findByText(/tôi là Thiên Hạc/)).toBeTruthy();
  });

  it("switches sessions from the history list", async () => {
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
      return Promise.resolve(jsonResponse(ACCESS));
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
      return Promise.resolve(jsonResponse(ACCESS));
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
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
          return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        }
        if (url.endsWith("/api/v1/sessions/s1")) {
          return Promise.resolve(jsonResponse({ session: sessionDetail("s1", []) }));
        }
        return Promise.resolve(jsonResponse(ACCESS));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText(/tôi là Thiên Hạc/);

    const button = screen.getByRole("button", { name: "Tạo mới" });
    expect((button as HTMLButtonElement).disabled).toBe(true);
  });

  it("aborts the active stream before switching sessions", async () => {
    let streamSignal: AbortSignal | undefined;
    let cancelled = false;
    let cancellationReads = 0;
    let balanceReads = 0;
    const encoder = new TextEncoder();
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith("/api/v1/me")) {
        balanceReads += 1;
        return Promise.resolve(jsonResponse({ ...ACCESS, balance: cancelled ? 6 : 3 }));
      }
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
        const messages = [message({ content: "tin từ s1" })];
        if (streamSignal?.aborted) {
          cancelled = ++cancellationReads > 1;
          messages.push(
            message({ id: "a2", content: "", status: cancelled ? "cancelled" : "pending" }),
          );
        }
        return Promise.resolve(jsonResponse({ session: sessionDetail("s1", messages) }));
      }
      if (url.endsWith("/api/v1/sessions/s2")) {
        return Promise.resolve(
          jsonResponse({ session: sessionDetail("s2", [message({ content: "tin từ s2" })]) }),
        );
      }
      return Promise.resolve(jsonResponse(ACCESS));
    });
    vi.stubGlobal("fetch", fetchMock);
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("tin từ s1");
    fireEvent.change(screen.getByPlaceholderText("Hỏi Thiên Hạc điều gì đó…"), {
      target: { value: "Câu hỏi đang chạy" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Gửi" }));
    await waitFor(() => expect(streamSignal).toBeDefined());

    fireEvent.click(screen.getByText("Lịch sử"));
    fireEvent.click(await screen.findByText(/Cuộc trò chuyện 28\/08/));

    expect(streamSignal?.aborted).toBe(true);
    expect(await screen.findByText("tin từ s2")).toBeTruthy();
    expect(screen.queryByText("Câu hỏi đang chạy")).toBeNull();
    await waitFor(() => expect(cancellationReads).toBe(1));
    expect(balanceReads).toBe(0);
    expect(screen.getByText("6 coins")).toBeTruthy();
    expect(screen.queryByText("3 coins")).toBeNull();
    await waitFor(() => expect(balanceReads).toBe(1), { timeout: 2500 });
    expect(cancelled).toBe(true);
    expect(screen.getByText("6 coins")).toBeTruthy();
  });

  it("explains the chat cost when the account has insufficient coins", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/api/v1/chart-profiles/p1/sessions")) {
          return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        }
        if (url.endsWith("/api/v1/sessions/s1/chat/stream")) {
          return Promise.resolve(jsonResponse({ detail: "Insufficient coins." }, 402));
        }
        if (url.endsWith("/api/v1/sessions/s1")) {
          return Promise.resolve(
            jsonResponse({
              session: sessionDetail("s1", [message({ content: "Previous reply" })]),
            }),
          );
        }
        return Promise.resolve(jsonResponse(ACCESS));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("Previous reply");
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "My question" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() =>
      expect(toastMocks.showToast).toHaveBeenCalledWith(
        "Not enough coins. AI chat costs 3 coins per message.",
      ),
    );
    expect((input as HTMLInputElement).disabled).toBe(false);
  });

  it("surfaces a backend error event and preserves partial text", async () => {
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
        return Promise.resolve(jsonResponse(ACCESS));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("tin đã gửi");
    fireEvent.change(screen.getByPlaceholderText("Hỏi Thiên Hạc điều gì đó…"), {
      target: { value: "Hỏi thử" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Gửi" }));

    expect(await screen.findByText("Phần trả lời")).toBeTruthy();
    await waitFor(() =>
      expect(toastMocks.showToast).toHaveBeenCalledWith(
        "Thiên Hạc chưa thể trả lời trọn vẹn. Bạn thử lại nhé.",
      ),
    );
    expect(screen.getByText("Tin nhắn chưa gửi trọn vẹn.")).toBeTruthy();
  });

  it("reconciles a duplicate in-progress stream from the stored assistant message", async () => {
    let detailCalls = 0;
    let balanceReads = 0;
    const stream =
      [
        'data: {"type":"duplicate_in_progress","user_message_id":"u2","assistant_message_id":"a2","status":"pending"}',
        'data: {"type":"done","status":"duplicate_in_progress"}',
      ].join("\n\n") + "\n\n";
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/api/v1/me")) {
          balanceReads += 1;
          return Promise.resolve(jsonResponse({ ...ACCESS, balance: 3 }));
        }
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
                  message({
                    id: "a2",
                    content: "Câu trả lời đã hoàn tất",
                    status: detailCalls > 2 ? "confirmed" : "pending",
                  }),
                ];
          return Promise.resolve(jsonResponse({ session: sessionDetail("s1", messages) }));
        }
        return Promise.resolve(jsonResponse(ACCESS));
      }),
    );
    setChart("p1");

    renderScreen(new QueryClient());
    await screen.findByText("tin đã gửi");
    fireEvent.change(screen.getByPlaceholderText("Hỏi Thiên Hạc điều gì đó…"), {
      target: { value: "Hỏi lại cùng key" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Gửi" }));

    expect(await screen.findByText("Câu trả lời đã hoàn tất", {}, { timeout: 2500 })).toBeTruthy();
    await waitFor(() => expect(balanceReads).toBeGreaterThanOrEqual(2));
    expect(screen.getByText("3 coins")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Gửi" }) as HTMLButtonElement).disabled).toBe(false);
  });

  it("issues only one create request for repeated activation while pending", async () => {
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
      return Promise.resolve(jsonResponse(ACCESS));
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
