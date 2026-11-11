import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

import type { ChartProfile } from "@/lib/api/schemas";
import chart from "@/lib/api/__fixtures__/build-laso.json";
import { useChartStore } from "@/store/chart-store";

import { SavedChartList } from "./saved-chart-list";

const mocks = vi.hoisted(() => ({ mutate: vi.fn(), hook: vi.fn(), push: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: mocks.push }) }));
vi.mock("@/lib/api/hooks", () => ({ useOpenChartProfile: mocks.hook }));
vi.mock("@/features/an-sao/casting-loader", () => ({
  CastingLoader: ({ title }: { title: string }) => <p>{title}</p>,
}));
vi.mock("./saved-chart-card", () => ({
  SavedChartCard: ({
    profile,
    onOpen,
  }: {
    profile: ChartProfile;
    onOpen: (profile: ChartProfile) => void;
  }) => (
    <article>
      <button onClick={() => onOpen(profile)}>{profile.display_name}</button>
    </article>
  ),
}));
const OPEN_PROFILE = { mutate: mocks.mutate, isPending: false, isSuccess: false, isError: false };
const profiles: ChartProfile[] = Array.from({ length: 15 }, (_, index) => ({
  id: `p${index + 1}`,
  display_name: index === 14 ? "Mẹ Mai" : `Chart ${index + 1}`,
  birth_info: { calendar: "solar", year: 2000 + index, month: 4, day: 15, hour: 8, gender: "M" },
  created_at: "2026-10-04T00:00:00Z",
  updated_at: "2026-10-04T00:00:00Z",
}));
let wide = false;
const listeners = new Set<() => void>();
const media = window.matchMedia("(min-width: 768px)");
beforeEach(() => {
  vi.clearAllMocks();
  mocks.hook.mockReturnValue(OPEN_PROFILE);
  useChartStore.getState().reset();
  wide = false;
  listeners.clear();
  vi.spyOn(window, "matchMedia").mockReturnValue({
    ...media,
    get matches() {
      return wide;
    },
    addEventListener: vi.fn((_event, listener: () => void) => listeners.add(listener)),
    removeEventListener: vi.fn((_event, listener: () => void) => listeners.delete(listener)),
  });
});
afterEach(() => vi.restoreAllMocks());
const names = () => screen.queryAllByRole("article").map((card) => card.textContent);
const pageInput = () => screen.getByRole("textbox", { name: "Số trang" }) as HTMLInputElement;
const search = (value: string) =>
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm lá số" }), { target: { value } });
function jump(value: string) {
  fireEvent.change(pageInput(), { target: { value } });
  fireEvent.keyDown(pageInput(), { key: "Enter" });
}

it("shows responsive page sizes and one top pagination bar", () => {
  render(<SavedChartList profiles={profiles} />);
  expect(window.matchMedia).toHaveBeenCalledWith("(min-width: 768px)");
  expect(names()).toHaveLength(3);
  expect(screen.getByRole("status").textContent).toBe("1–3 / 15 lá số");
  const navigation = screen.getAllByRole("navigation", { name: "Phân trang lá số" });
  expect(navigation).toHaveLength(1);
  const firstCard = screen.getAllByRole("article")[0]!;
  expect(navigation[0]!.compareDocumentPosition(firstCard)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  const input = pageInput();
  expect(input.labels?.[0]).toBe(input.parentElement);
  fireEvent.focus(input);
  expect([input.selectionStart, input.selectionEnd]).toEqual([0, input.value.length]);
  for (const matches of [true, false]) {
    act(() => {
      wide = matches;
      listeners.forEach((notify) => notify());
    });
    expect(names()).toHaveLength(matches ? 4 : 3);
  }
});

it("searches off-page names and birth dates, resets pagination and clears empty results", () => {
  render(<SavedChartList profiles={profiles} />);
  jump("3");
  search("  ME   MAI  ");
  expect(names()).toEqual(["Mẹ Mai"]);
  expect(screen.getByRole("status").textContent).toBe("1–1 / 1 lá số phù hợp");
  for (const query of ["15/04/2012", "2012"]) {
    search(query);
    expect(names()).toEqual(["Chart 13"]);
  }
  search("missing");
  expect(names()).toEqual([]);
  expect(screen.getByText(/Không tìm thấy lá số/)).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Xóa tìm kiếm" }));
  expect(names()).toEqual(["Chart 1", "Chart 2", "Chart 3"]);
});

it("accepts Enter or blur page jumps and rejects invalid drafts", () => {
  render(<SavedChartList profiles={profiles} />);
  expect(pageInput().type).toBe("text");
  expect(pageInput().inputMode).toBe("numeric");
  jump("2");
  for (const value of ["", "0", "-1", "1.5", "1e1", "text", "6"]) {
    jump(value);
    expect(screen.getByRole("alert").textContent).toBe("Nhập số nguyên từ 1 đến 5.");
    expect(names()).toEqual(["Chart 4", "Chart 5", "Chart 6"]);
  }
  fireEvent.change(pageInput(), { target: { value: "3" } });
  fireEvent.blur(pageInput());
  expect(names()).toEqual(["Chart 7", "Chart 8", "Chart 9"]);
  expect(screen.queryByRole("alert")).toBeNull();
});

it("keeps drafts pending and respects page boundaries", () => {
  render(<SavedChartList profiles={profiles} />);
  const previous = screen.getByRole("button", { name: "Trang trước" }) as HTMLButtonElement;
  const next = screen.getByRole("button", { name: "Trang sau" }) as HTMLButtonElement;
  expect(previous.disabled).toBe(true);
  fireEvent.change(pageInput(), { target: { value: "2" } });
  expect(names()).toEqual(["Chart 1", "Chart 2", "Chart 3"]);
  jump("5");
  expect(names()).toEqual(["Chart 13", "Chart 14", "Mẹ Mai"]);
  expect(next.disabled).toBe(true);
  fireEvent.click(previous);
  expect(pageInput().value).toBe("4");
  expect(names()).toEqual(["Chart 10", "Chart 11", "Chart 12"]);
});

it("clamps deletion pages and updates active rename searches", () => {
  const view = render(<SavedChartList profiles={profiles} />);
  jump("5");
  const remaining = profiles.slice(0, 7);
  view.rerender(<SavedChartList profiles={remaining} />);
  expect(pageInput().value).toBe("3");
  expect(names()).toEqual(["Chart 7"]);
  search("mai");
  const renamed = remaining.map((profile, index) =>
    index === 6 ? { ...profile, display_name: "Mai" } : profile,
  );
  view.rerender(<SavedChartList profiles={renamed} />);
  expect(names()).toEqual(["Mai"]);
  view.rerender(<SavedChartList profiles={remaining} />);
  expect(names()).toEqual([]);
});

it("activates the selected profile only after loading and redirects to Ban Menh", () => {
  const content = () => (
    <>
      <h1>Hồ sơ</h1>
      <SavedChartList profiles={profiles} />
    </>
  );
  const view = render(content());
  fireEvent.click(screen.getByRole("button", { name: "Chart 2" }));
  const [profile, callbacks] = mocks.mutate.mock.calls[0]!;
  expect(profile).toBe(profiles[1]);
  expect(useChartStore.getState().hasChart).toBe(false);
  mocks.hook.mockReturnValue({ ...OPEN_PROFILE, isPending: true });
  view.rerender(content());
  const loading = screen.getByRole("dialog", { name: "Đang mở lá số đã lưu" });
  expect(view.container.contains(loading)).toBe(false);
  expect(loading.className).toContain("fixed inset-0 z-55");
  expect(loading.className).toContain("bg-bg-0");
  expect(screen.queryByRole("heading", { name: "Hồ sơ" })).toBeNull();
  expect(screen.getByRole("status", { name: "Đang mở lá số đã lưu" })).toBeTruthy();
  expect(screen.queryAllByRole("article")).toHaveLength(0);
  fireEvent.keyDown(loading, { key: "Escape" });
  expect(screen.getByRole("dialog")).toBe(loading);
  act(() => callbacks.onSuccess({ chart }));
  expect(useChartStore.getState()).toMatchObject({
    hasChart: true,
    chartId: chart.id,
    chartProfileId: profile.id,
    birthInfo: profile.birth_info,
  });
  expect(mocks.push).toHaveBeenCalledWith("/ban-menh");
  mocks.hook.mockReturnValue({ ...OPEN_PROFILE, isSuccess: true });
  view.rerender(content());
  expect(screen.getByRole("dialog")).toBe(loading);
});

it("restores the list and focus for retry without changing the active chart on failure", async () => {
  useChartStore.getState().castChart({ stars: [] }, "previous", profiles[0]!.birth_info, "p1");
  const view = render(<SavedChartList profiles={profiles} />);
  const selected = screen.getByRole("button", { name: "Chart 2" });
  selected.focus();
  fireEvent.click(selected);
  mocks.hook.mockReturnValue({ ...OPEN_PROFILE, isPending: true });
  view.rerender(<SavedChartList profiles={profiles} />);
  expect(screen.getByRole("dialog")).toBeTruthy();
  mocks.hook.mockReturnValue({ ...OPEN_PROFILE, isError: true, error: new Error("Load failed") });
  view.rerender(<SavedChartList profiles={profiles} />);
  expect(screen.queryByRole("dialog")).toBeNull();
  await waitFor(() => expect(document.activeElement).toBe(selected));
  expect(screen.getByRole("alert").textContent).toContain("Không mở được lá số");
  expect(useChartStore.getState().chartId).toBe("previous");
  fireEvent.click(screen.getByRole("button", { name: "Chart 2" }));
  expect(mocks.mutate).toHaveBeenCalledTimes(2);
  expect(mocks.mutate).toHaveBeenCalledWith(profiles[1], expect.any(Object));
  expect(mocks.push).not.toHaveBeenCalled();
});
