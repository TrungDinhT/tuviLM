import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, renderHook, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CapabilityReport } from "./nang-luc-screen";
import {
  capabilityKey,
  capabilitySchema,
  useCapabilityReport,
  useCapabilityStore,
  type CapabilityProfile,
} from "./data";
import { useChartStore } from "@/store/chart-store";
const birth = {
  calendar: "solar" as const,
  year: 1996,
  month: 4,
  day: 15,
  hour: 10,
  gender: "M" as const,
};
const report: CapabilityProfile = {
  tong_quan: "Cấu trúc Mệnh của bạn.",
  diem_manh: [
    {
      nang_luc_id: "lap_luan_logic",
      nang_luc: "Lập luận logic",
      mo_ta: "Bạn suy nghĩ thấu đáo.",
      giai_thich: "Luận giải chuyên sâu từ lá số.",
    },
  ],
  diem_yeu: [],
};
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));
beforeEach(() => {
  // jsdom does not provide layout observers; geometry is checked in a browser.
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
function wrapper({ children }: { children: React.ReactNode }) {
  return <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>;
}
describe("capability report", () => {
  it("accepts independent empty lists and rejects malformed findings", () => {
    expect(capabilitySchema.safeParse(report).success).toBe(true);
    expect(capabilitySchema.safeParse({ ...report, diem_yeu: [{ ten: "A" }] }).success).toBe(false);
  });
  it("opens the full explanation and handles an empty caution section", () => {
    render(<CapabilityReport report={report} />);
    expect(screen.getByText(/Chưa có đủ cơ sở/)).toBeTruthy();
    expect(screen.queryByText(report.diem_manh[0]!.mo_ta)).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Xem luận giải: Lập luận logic" }));
    expect(screen.getByRole("dialog").textContent).toContain(report.diem_manh[0]!.mo_ta);
    expect(screen.getByRole("dialog").textContent).toContain("Luận giải chuyên sâu từ lá số.");
    fireEvent.click(screen.getByText("Đóng luận giải"));
    expect(screen.queryByRole("dialog")).toBeNull();
  });
  it("dims other findings and restores them and focus after closing the drawer", async () => {
    const second = { ...report.diem_manh[0]!, nang_luc_id: "phan_bien", nang_luc: "Phản biện" };
    render(<CapabilityReport report={{ ...report, diem_manh: [...report.diem_manh, second] }} />);
    const firstButton = screen.getByRole("button", { name: "Xem luận giải: Lập luận logic" });
    const otherButton = screen.getByRole("button", { name: "Xem luận giải: Phản biện" });
    firstButton.focus();
    fireEvent.click(firstButton);
    expect(firstButton.getAttribute("data-selected")).toBe("true");
    expect(firstButton.getAttribute("data-dimmed")).toBe("false");
    expect(otherButton.getAttribute("data-dimmed")).toBe("true");
    fireEvent.click(screen.getByText("Đóng luận giải"));
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(otherButton.getAttribute("data-dimmed")).toBe("false");
    await waitFor(() => expect(document.activeElement).toBe(firstButton));
  });
  it("opens the overview in the same drawer and dismisses it with Escape", async () => {
    render(<CapabilityReport report={report} />);
    const center = screen.getByRole("button", { name: "Thấu hiểu cấu trúc Mệnh" });
    const strength = screen.getByRole("button", { name: "Xem luận giải: Lập luận logic" });
    center.focus();
    fireEvent.click(center);
    expect(screen.getByRole("dialog").textContent).toContain(report.tong_quan);
    expect(strength.getAttribute("data-dimmed")).toBe("true");
    fireEvent.keyDown(screen.getByRole("dialog"), { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(strength.getAttribute("data-dimmed")).toBe("false");
  });
  it("does not request a locked report", () => {
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);
    renderHook(() => useCapabilityReport(birth, false), { wrapper });
    expect(fetch).not.toHaveBeenCalled();
  });
  it("uses a restored report without calling the backend", async () => {
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);
    const key = capabilityKey(birth);
    useCapabilityStore.getState().unlock(key);
    useCapabilityStore.getState().save(key, report);
    const { result } = renderHook(() => useCapabilityReport(birth, true), { wrapper });
    await waitFor(() => expect(result.current.data).toEqual(report));
    expect(fetch).not.toHaveBeenCalled();
  });
  it("requests only the selected birth tuple and persists the result", async () => {
    const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(report)));
    vi.stubGlobal("fetch", fetch);
    const key = capabilityKey(birth);
    useCapabilityStore.getState().unlock(key);
    const { result } = renderHook(() => useCapabilityReport(birth, true), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(JSON.parse(fetch.mock.calls[0]?.[1].body)).toEqual(birth);
    expect(useCapabilityStore.getState().entries[key]?.report).toEqual(report);
    expect(
      useCapabilityStore.getState().entries[capabilityKey({ ...birth, hour: 11 })],
    ).toBeUndefined();
  });
  it("clears unlocks on chart reset and ignores a late report", () => {
    const key = capabilityKey(birth);
    useCapabilityStore.getState().unlock(key);
    useChartStore.getState().reset();
    useCapabilityStore.getState().save(key, report);
    expect(useCapabilityStore.getState().entries).toEqual({});
  });
});
