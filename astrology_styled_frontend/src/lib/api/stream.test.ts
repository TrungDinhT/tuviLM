import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { OWNER_ID_KEY, resetOwnerIdCache } from "@/lib/api/owner";
import { isApiError } from "@/lib/http/errors";

import type { SseChatEvent } from "./schemas";
import { parseSseStream, streamChat } from "./stream";

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
  resetOwnerIdCache();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("streamChat", () => {
  it("uses the logical turn's idempotency key and abort signal", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
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
        headers: expect.objectContaining({ "Idempotency-Key": "turn-key-1" }),
      }),
    );
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
