import { Effect, Stream } from "effect";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { isApiError } from "@/lib/http/errors";

import { runApi } from "./client";
import type { SseChatEvent } from "./schemas";
import { sentRequest } from "./sent-request";
import { chatEvents, sseEvents } from "./stream";

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

function parse(body: ReadableStream<Uint8Array>) {
  return sseEvents(Stream.fromReadableStream({ evaluate: () => body, onError: (error) => error }));
}

async function collect(body: ReadableStream<Uint8Array>): Promise<SseChatEvent[]> {
  return Effect.runPromise(Stream.runCollect(parse(body)));
}

/** Run one chat turn to completion, collecting its events. */
function runTurn(
  sessionId: string,
  content: string,
  opts: { idempotencyKey: string; signal?: AbortSignal; expectedUserId?: string | null },
): Promise<SseChatEvent[]> {
  const { signal, ...rest } = opts;
  return runApi(Stream.runCollect(chatEvents(sessionId, content, rest)), signal);
}

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("chatEvents", () => {
  it("does not open a stream while signed out", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    await expect(
      runTurn("session-a", "Account A message", {
        idempotencyKey: "turn-a",
        expectedUserId: null,
      }),
    ).rejects.toMatchObject({ error: { kind: "http", status: 401 } });
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it("does not open a stream after its account left", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const controller = new AbortController();
    controller.abort();
    await expect(
      runTurn("s1", "Hello", { idempotencyKey: "turn-1", signal: controller.signal }),
    ).rejects.toMatchObject({ name: "AbortError" });
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it("uses the logical turn's idempotency key, abort signal and expected account", async () => {
    const controller = new AbortController();
    const fetchMock = vi.fn().mockResolvedValue(
      new Response('data: {"type":"done","status":"confirmed"}\n\n', {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const events = await runTurn("s1", "xin chào", {
      idempotencyKey: "turn-key-1",
      signal: controller.signal,
      expectedUserId: "account-a",
    });

    expect(events).toEqual([{ type: "done", status: "confirmed" }]);
    const sent = sentRequest(fetchMock.mock.calls[0]);
    expect(sent).toMatchObject({
      path: "/api/v1/sessions/s1/chat/stream",
      method: "POST",
      body: { content: "xin chào" },
    });
    expect(Object.fromEntries(sent.headers)).toEqual({
      "content-type": "application/json",
      "idempotency-key": "turn-key-1",
      "x-expected-user-id": "account-a",
    });
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

    await expect(runTurn("s1", "Hello", { idempotencyKey: "turn-1" })).rejects.toMatchObject({
      error: { kind: "http", status: 402, body },
    });
  });
});

describe("sseEvents", () => {
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

    let caught: unknown;
    try {
      await Effect.runPromise(Stream.runCollect(parse(body)));
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
