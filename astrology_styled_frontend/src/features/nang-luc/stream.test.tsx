import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { NangLucScreen } from "./nang-luc-screen";
import { useCapabilityStore, capabilityKey, type CapabilityProfile } from "./data";
import { streamCapabilityReport } from "./stream";
import { useChartStore } from "@/store/chart-store";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));
const birth = {
  calendar: "solar" as const,
  year: 1998,
  month: 4,
  day: 4,
  hour: 8,
  gender: "M" as const,
};
const first = {
  nang_luc_id: "lap_luan_logic",
  nang_luc: "Lập luận logic",
  mo_ta: "Mô tả",
  giai_thich: "Luận giải",
};
const second = { ...first, nang_luc_id: "phan_bien", nang_luc: "Phản biện" };
const profile: CapabilityProfile = {
  tong_quan: "Tổng quan",
  diem_manh: [first, second],
  diem_yeu: [],
};
beforeEach(() => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  useCapabilityStore.getState().clear();
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("reveals each finding before completion, preserves the drawer, and persists only done", async () => {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const body = new ReadableStream<Uint8Array>({
    start(value) {
      controller = value;
    },
  });
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(body)));
  const emit = async (event: object) => {
    await act(async () =>
      controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(event)}\n\n`)),
    );
  };
  const client = new QueryClient();
  useChartStore.getState().castChart({ stars: ["tuvi"] }, "test", birth);
  useCapabilityStore.getState().unlock(capabilityKey(birth));
  render(
    <QueryClientProvider client={client}>
      <NangLucScreen />
    </QueryClientProvider>,
  );
  await emit({ type: "started", attempt: 0 });
  await emit({ type: "finding", attempt: 0, kind: "strength", index: 0, id: "s0", finding: first });
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "Xem luận giải: Lập luận logic" })).toBeTruthy(),
  );
  expect(useCapabilityStore.getState().entries[capabilityKey(birth)]?.report).toBeUndefined();
  expect(screen.queryByText(/Chưa có đủ cơ sở/)).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Xem luận giải: Lập luận logic" }));
  await emit({
    type: "finding",
    attempt: 0,
    kind: "strength",
    index: 1,
    id: "s1",
    finding: second,
  });
  await waitFor(() =>
    expect(document.querySelector('[data-layout-id="strength:phan_bien"]')).toBeTruthy(),
  );
  expect(screen.getByRole("dialog").textContent).toContain("Lập luận logic");
  await emit({ type: "done", attempt: 0, profile });
  await waitFor(() =>
    expect(useCapabilityStore.getState().entries[capabilityKey(birth)]?.report).toEqual(profile),
  );
  expect(screen.getByRole("dialog").textContent).toContain("Luận giải");
  cleanup();
  client.clear();
});

it("decodes fragmented UTF-8, CRLF, comments and rejects an incomplete stream", async () => {
  const wire = new TextEncoder().encode(
    `: ping\r\n\r\ndata: ${JSON.stringify({ type: "started", attempt: 0 })}\r\n\r\ndata: ${JSON.stringify({ type: "done", attempt: 0, profile })}\r\n\r\n`,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(
        new ReadableStream({
          start(controller) {
            for (const byte of wire) controller.enqueue(new Uint8Array([byte]));
            controller.close();
          },
        }),
      ),
    ),
  );
  expect(await streamCapabilityReport(birth, new AbortController().signal, () => {})).toEqual(
    profile,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(new Response('data: {"type":"started","attempt":0}\n\n')),
  );
  await expect(
    streamCapabilityReport(birth, new AbortController().signal, () => {}),
  ).rejects.toThrow("gián đoạn");
});

it("clears provisional cards on reset and leaves failed output out of persisted reports", async () => {
  const frames = [
    { type: "started", attempt: 0 },
    { type: "finding", attempt: 0, kind: "strength", index: 0, id: "s0", finding: first },
    { type: "reset", attempt: 1 },
    { type: "error", message: "Không thể hoàn tất." },
  ];
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue(
        new Response(frames.map((event) => `data: ${JSON.stringify(event)}\n\n`).join("")),
      ),
  );
  const client = new QueryClient();
  useChartStore.getState().castChart({ stars: ["tuvi"] }, "test", birth);
  useCapabilityStore.getState().unlock(capabilityKey(birth));
  render(
    <QueryClientProvider client={client}>
      <NangLucScreen />
    </QueryClientProvider>,
  );
  await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
  expect(screen.queryByRole("button", { name: "Xem luận giải: Lập luận logic" })).toBeNull();
  expect(useCapabilityStore.getState().entries[capabilityKey(birth)]?.report).toBeUndefined();
  cleanup();
  client.clear();
});
