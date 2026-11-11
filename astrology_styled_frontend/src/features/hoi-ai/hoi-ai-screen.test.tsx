import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
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
    const fetchMock = mockBillingChat('data: {"type":"done","status":"confirmed"}\n\n', () => ({
      ...ACCESS,
      plan: "full_unlock",
      balance: 0,
    }));
    renderScreen(new QueryClient(), true);
    expect(
      await screen.findByText("Trò chuyện với AI đã được bao gồm trong gói Mở khóa toàn bộ."),
    ).toBeTruthy();
    expect(screen.getByText("Mở khóa toàn bộ")).toBeTruthy();
    expect(screen.queryByText(/xu|1\.234|1234/i)).toBeNull();
    expect(screen.queryByLabelText("Số dư tài khoản")).toBeNull();
    expect(screen.getByLabelText("Mở khóa toàn bộ").getAttribute("title") ?? "").not.toMatch(
      /xu|1\.234|1234/i,
    );
    await screen.findByText("Previous reply");
    expect((screen.getByRole("textbox") as HTMLInputElement).disabled).toBe(false);
    await sendQuestion();
    await waitFor(() =>
      expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/chat/stream"))).toBe(true),
    );
  });

  it("blocks sending with fewer than three coins without adding a draft", async () => {
    const fetchMock = mockBillingChat("", () => ({ ...ACCESS, balance: 2 }));
    renderScreen(new QueryClient(), true);
    await screen.findByText("Previous reply");
    await screen.findByText(/Bạn không đủ xu/);
    const input = screen.getByRole("textbox") as HTMLInputElement;
    expect(input.disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Gửi" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.change(input, { target: { value: "My question" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/chat/stream"))).toBe(false);
    expect(screen.queryByText("My question")).toBeNull();
    expect(screen.queryByText("Tin nhắn chưa gửi trọn vẹn.")).toBeNull();
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
    await screen.findByText("6 xu");
    expect(
      screen.getByText("Trò chuyện với AI: 3 xu mỗi tin nhắn. Chỉ trừ xu khi AI trả lời hoàn tất."),
    ).toBeTruthy();
    await sendQuestion();
    await screen.findByText("Working reply");
    expect(screen.getByText("6 xu")).toBeTruthy();
    expect(reads).toBe(1);
    finish();
    expect(await screen.findByText("3 xu")).toBeTruthy();
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
    await screen.findByText("6 xu");
    await sendQuestion();
    await waitFor(() => expect(reads).toBe(2));
    expect(screen.getByText("6 xu")).toBeTruthy();
    expect((screen.getByRole("textbox") as HTMLInputElement).disabled).toBe(false);
  });

  it("asks guests to sign in without fetching private sessions", () => {
    accountState.data = null;
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    setChart("legacy-profile");

    renderScreen(new QueryClient());

    expect(screen.getByText("Đăng nhập để lưu lá số và trò chuyện với AI.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Đăng nhập" }).getAttribute("href")).toBe("/login");
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

  it("drops the selected session and draft when the saved chart changes", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { staleTime: Infinity } } });
    const detail = (id: string) => ({
      ...sessionDetail(id, [message({ content: `Reply from ${id}` })]),
      chart_profile_id: id === "s3" ? "p2" : "p1",
    });
    client.setQueryData(queryKeys.sessions.byProfile("p1"), { sessions: SESSIONS });
    client.setQueryData(queryKeys.sessions.byProfile("p2"), {
      sessions: [{ ...SESSIONS[0], id: "s3", chart_profile_id: "p2" }],
    });
    for (const id of ["s1", "s2", "s3"]) {
      client.setQueryData(queryKeys.sessions.detail(id), { session: detail(id) });
    }
    const stream =
      'data: {"type":"text","delta":"Old draft"}\n\ndata: {"type":"done","status":"failed"}\n\n';
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.endsWith("/chat/stream")) return Promise.resolve(new Response(stream));
        if (url.endsWith("/sessions")) return Promise.resolve(jsonResponse({ sessions: SESSIONS }));
        if (url.endsWith("/api/v1/me")) return Promise.resolve(jsonResponse(ACCESS));
        return Promise.resolve(jsonResponse({ session: detail(url.split("/").at(-1)!) }));
      }),
    );
    setChart("p1");
    renderScreen(client);
    fireEvent.click(screen.getByText("Lịch sử"));
    fireEvent.click(await screen.findByText(/Cuộc trò chuyện 28\/08/));
    await screen.findByText("Reply from s2");
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Old question" } });
    fireEvent.keyDown(screen.getByRole("textbox"), { key: "Enter" });
    await screen.findByText("Old draft");
    fireEvent.click(screen.getByText("Lịch sử"));

    act(() => setChart("p2"));

    expect(await screen.findByText("Reply from s3")).toBeTruthy();
    expect(screen.queryByText("Reply from s2")).toBeNull();
    expect(screen.queryByText("Old draft")).toBeNull();
    expect(screen.queryByText("Old question")).toBeNull();
    expect(screen.queryByRole("dialog")).toBeNull();
    expect((screen.getByRole("textbox") as HTMLInputElement).value).toBe("");
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
    expect(screen.getByText("6 xu")).toBeTruthy();
    expect(screen.queryByText("3 xu")).toBeNull();
    await waitFor(() => expect(balanceReads).toBe(1), { timeout: 2500 });
    expect(cancelled).toBe(true);
    expect(screen.getByText("6 xu")).toBeTruthy();
  });

  it("removes the draft when the server rejects a stale balance with insufficient coins", async () => {
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
        "Bạn không đủ xu. Trò chuyện với AI cần 3 xu cho mỗi tin nhắn.",
      ),
    );
    expect((input as HTMLInputElement).disabled).toBe(false);
    expect(screen.queryByText("My question")).toBeNull();
    expect(screen.queryByText("Tin nhắn chưa gửi trọn vẹn.")).toBeNull();
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
    expect(screen.getByText("3 xu")).toBeTruthy();
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
