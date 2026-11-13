import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useChartStore } from "@/store/chart-store";
import { usePreferencesStore } from "@/store/preferences-store";

import { AnSaoScreen } from "./an-sao-screen";

const { previewData, castChart, useMutation, castChartMutationOptions, toast, push } = vi.hoisted(
  () => ({
    previewData: { chinh_tinh: ["Tham Lang"] },
    castChart: { mutate: vi.fn(), isPending: false, isSuccess: false },
    useMutation: vi.fn(),
    castChartMutationOptions: vi.fn(),
    toast: vi.fn(),
    push: vi.fn(),
  }),
);

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/toast", () => ({ showToast: toast, dismissToast: vi.fn() }));

vi.mock("@/lib/api/laso", () => ({
  castChartMutationOptions,
  lasoPreviewQueryOptions: ({ birth }: { birth: { hour?: number } | null }) => ({ birth }),
}));

vi.mock("@tanstack/react-query", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@tanstack/react-query")>()),
  useMutation,
  useQuery: ({ birth }: { birth: { hour?: number } | null }) => ({
    data: birth === null ? undefined : previewData,
    isPlaceholderData: birth?.hour === 4,
  }),
}));

beforeEach(() => {
  vi.clearAllMocks();
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  useMutation.mockReturnValue(castChart);
  usePreferencesStore.setState({ muteBirthConfirm: false });
  useChartStore.getState().reset();
});

afterEach(() => vi.unstubAllGlobals());

describe("AnSaoScreen hierarchy", () => {
  it("prefills saved birth data without changing it when casting again", () => {
    usePreferencesStore.setState({ muteBirthConfirm: true });
    for (const hour of [0, 12, 22]) {
      const birth = {
        calendar: "solar" as const,
        year: 1996,
        month: 4,
        day: 15,
        hour,
        gender: "F" as const,
      };
      useChartStore.setState({ birthInfo: birth });
      const view = render(<AnSaoScreen />);
      expect(
        screen.getByRole("radio", { name: hour < 12 ? "AM" : "PM" }).getAttribute("aria-checked"),
      ).toBe("true");
      expect(screen.getByRole("radio", { name: "Nữ" }).getAttribute("aria-checked")).toBe("true");
      fireEvent.click(screen.getByRole("button", { name: /Luận giải lá số của tôi/ }));
      expect(castChart.mutate).toHaveBeenLastCalledWith(birth, expect.any(Object));
      view.unmount();
    }
  });

  it("holds the loader for the loading interlude and only navigates on success", () => {
    usePreferencesStore.setState({ muteBirthConfirm: true });
    const view = render(<AnSaoScreen />);
    expect(castChartMutationOptions).toHaveBeenCalledWith(
      expect.objectContaining({ minDurationMs: 2600 }),
    );
    fireEvent.keyDown(screen.getByRole("slider", { name: "Giờ sinh" }), { key: "ArrowRight" });
    fireEvent.click(screen.getByRole("radio", { name: "Nam" }));
    fireEvent.click(screen.getByRole("button", { name: /Luận giải lá số của tôi/ }));
    const [, callbacks] = castChart.mutate.mock.calls[0]!;

    for (const state of [{ isPending: true }, { isSuccess: true }]) {
      useMutation.mockReturnValue({ ...castChart, ...state });
      view.rerender(<AnSaoScreen />);
      expect(screen.queryByRole("button", { name: /Luận giải lá số của tôi/ })).toBeNull();
    }
    // The hook activates the chart; the screen only navigates.
    expect(push).not.toHaveBeenCalled();
    act(() => callbacks.onSuccess());
    expect(push).toHaveBeenCalledWith("/ban-menh");
  });

  it("returns to the form and reports a failed cast", () => {
    usePreferencesStore.setState({ muteBirthConfirm: true });
    const view = render(<AnSaoScreen />);
    fireEvent.keyDown(screen.getByRole("slider", { name: "Giờ sinh" }), { key: "ArrowRight" });
    fireEvent.click(screen.getByRole("radio", { name: "Nam" }));
    fireEvent.click(screen.getByRole("button", { name: /Luận giải lá số của tôi/ }));
    const [, callbacks] = castChart.mutate.mock.calls[0]!;
    useMutation.mockReturnValue({ ...castChart, isPending: true });
    view.rerender(<AnSaoScreen />);

    useMutation.mockReturnValue(castChart);
    view.rerender(<AnSaoScreen />);
    act(() => callbacks.onError(new Error("build failed")));
    expect(screen.getByRole("button", { name: /Luận giải lá số của tôi/ })).toBeTruthy();
    expect(toast).toHaveBeenCalledWith("Có lỗi xảy ra khi an sao. Bạn thử lại nhé.");
    expect(push).not.toHaveBeenCalled();
  });

  it("puts the primary action before the atmospheric reward in reading order", () => {
    render(<AnSaoScreen />);
    const brand = screen.getByRole("link", { name: "Thiên Hạc — về trang chủ" });
    expect(brand.getAttribute("href")).toBe("/");
    expect(brand.querySelector("img")?.getAttribute("src")).toContain("favicon-48x48.png");

    const action = screen.getByRole("button", { name: /Luận giải lá số của tôi/ });
    const reward = screen.getByText("CHÒM SAO MỆNH ĐANG NGỦ").parentElement;

    expect(reward).not.toBeNull();
    expect(action.compareDocumentPosition(reward as HTMLElement)).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
  });

  it("replays a same-god constellation when the selected birth hour changes", () => {
    vi.useFakeTimers();
    try {
      render(<AnSaoScreen />);
      const clock = screen.getByRole("slider", { name: "Giờ sinh" });

      fireEvent.keyDown(clock, { key: "ArrowRight" });
      act(() => vi.advanceTimersByTime(250));
      const firstReveal = screen.getByRole("img", { name: /Tham Lang/ });

      fireEvent.keyDown(clock, { key: "ArrowRight" });
      expect(screen.getByRole("img", { name: /Tham Lang/ })).toBe(firstReveal);

      act(() => vi.advanceTimersByTime(250));

      expect(screen.getByRole("img", { name: /Tham Lang/ })).not.toBe(firstReveal);
    } finally {
      vi.useRealTimers();
    }
  });

  it("keeps the previous god static while the next preview is pending", () => {
    vi.useFakeTimers();
    try {
      render(<AnSaoScreen />);
      const clock = screen.getByRole("slider", { name: "Giờ sinh" });

      fireEvent.keyDown(clock, { key: "ArrowRight" });
      act(() => vi.advanceTimersByTime(250));
      const settledGod = screen.getByRole("img", { name: /Tham Lang/ });

      fireEvent.keyDown(clock, { key: "ArrowRight" });
      fireEvent.keyDown(clock, { key: "ArrowRight" });
      act(() => vi.advanceTimersByTime(250));

      expect(screen.getByRole("img", { name: /Tham Lang/ })).toBe(settledGod);
    } finally {
      vi.useRealTimers();
    }
  });
});
