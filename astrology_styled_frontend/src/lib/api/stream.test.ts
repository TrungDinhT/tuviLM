import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { authClient } from "@/lib/auth-client";
import { isApiError } from "@/lib/http/errors";

import type { SseChatEvent } from "./schemas";
import { parseSseStream, streamChat } from "./stream";

vi.mock("@/lib/auth-client", () => ({ authClient: { token: vi.fn() } }));

function sseBody(chunks: (string | Uint8Array)[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(typeof chunk === "string" ? encoder.encode(chunk) : chunk);
      }
      controller.close();
    },
  });
}

async function collect(body: ReadableStream<Uint8Array>): Promise<SseChatEvent[]> {
  const events: SseChatEvent[] = [];
  for await (const event of parseSseStream(body)) events.push(event);
  return events;
}

beforeEach(() => {
  localStorage.clear();
  vi.mocked(authClient.token).mockReset();
  vi.mocked(authClient.token).mockResolvedValue({ data: { token: "signed-token" }, error: null });
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("streamChat", () => {
  it("does not stream account A's message using account B's token", async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: "header.eyJzdWIiOiJhY2NvdW50LWIifQ.signature" },
      error: null,
    });
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    await expect(
      streamChat("session-a", "Account A message", {
        idempotencyKey: "turn-a",
        expectedUserId: "account-a",
      }).next(),
    ).rejects.toMatchObject({ error: { kind: "http", status: 401 } });
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it("does not open a stream if its account leaves while the token loads", async () => {
    let resolveToken!: (value: { data: { token: string }; error: null }) => void;
    vi.mocked(authClient.token).mockReturnValue(
      new Promise((resolve) => {
        resolveToken = resolve;
      }),
    );
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const controller = new AbortController();
    const pending = streamChat("s1", "Hello", {
      idempotencyKey: "turn-1",
      signal: controller.signal,
    }).next();
    const rejected = expect(pending).rejects.toMatchObject({ name: "AbortError" });
    controller.abort();
    resolveToken({ data: { token: "new-account-token" }, error: null });
    await rejected;
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it("uses the logical turn's idempotency key and abort signal", async () => {
    const controller = new AbortController();
    const fetchMock = vi.fn().mockResolvedValue(
      new Response('data: {"type":"done","status":"confirmed"}\n\n', {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const events: SseChatEvent[] = [];
    for await (const event of streamChat("s1", "xin chào", {
      idempotencyKey: "turn-key-1",
      signal: controller.signal,
    })) {
      events.push(event);
    }

    expect(events).toEqual([{ type: "done", status: "confirmed" }]);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/sessions/s1/chat/stream"),
      expect.objectContaining({
        signal: controller.signal,
        headers: {
          Authorization: "Bearer signed-token",
          "Content-Type": "application/json",
          "Idempotency-Key": "turn-key-1",
        },
      }),
    );
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(localStorage.length).toBe(0);
  });

  it("preserves an insufficient-coins response before streaming", async () => {
    const body = { detail: "Not enough coins. AI chat costs 3 coins per message." };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(body), {
          status: 402,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(
      streamChat("s1", "Hello", { idempotencyKey: "turn-1" }).next(),
    ).rejects.toMatchObject({ error: { kind: "http", status: 402, body } });
  });
});

describe("parseSseStream", () => {
  it("yields each typed event in order", async () => {
    const body = sseBody([
      'data: {"type":"ids","user_message_id":"u1","assistant_message_id":"a1"}\n\n',
      'data: {"type":"text","delta":"xin"}\n\n',
      'data: {"type":"text","delta":" chào"}\n\n',
      'data: {"type":"done","status":"confirmed"}\n\n',
    ]);

    expect(await collect(body)).toEqual([
      { type: "ids", user_message_id: "u1", assistant_message_id: "a1" },
      { type: "text", delta: "xin" },
      { type: "text", delta: " chào" },
      { type: "done", status: "confirmed" },
    ]);
  });

  it("reassembles a frame split across chunk boundaries", async () => {
    const body = sseBody(['data: {"type":"text","de', 'lta":"thiên', ' hạc"}\n', "\n"]);

    expect(await collect(body)).toEqual([{ type: "text", delta: "thiên hạc" }]);
  });

  it("decodes a UTF-8 character split across two chunks", async () => {
    // "ê" is U+00EA, encoded as the two bytes 0xC3 0xAA. Split them apart.
    const encoder = new TextEncoder();
    const body = sseBody([
      encoder.encode('data: {"type":"text","delta":"thi'),
      new Uint8Array([0xc3]),
      new Uint8Array([0xaa]),
      encoder.encode('n hạc"}\n\n'),
    ]);

    expect(await collect(body)).toEqual([{ type: "text", delta: "thiên hạc" }]);
  });

  it("ignores a frame with no data line", async () => {
    const body = sseBody([": heartbeat\n\n", 'data: {"type":"done","status":"confirmed"}\n\n']);

    expect(await collect(body)).toEqual([{ type: "done", status: "confirmed" }]);
  });

  it("throws a stream error for an unrecognised event", async () => {
    const body = sseBody(['data: {"type":"bogus"}\n\n']);

    const iterable = parseSseStream(body);
    let caught: unknown;
    try {
      await iterable.next();
    } catch (error) {
      caught = error;
    }

    expect(isApiError(caught)).toBe(true);
    if (isApiError(caught)) {
      expect(caught.error.kind).toBe("stream");
      if (caught.error.kind === "stream") {
        expect(caught.error.event).toContain('"bogus"');
      }
    }
  });
});
