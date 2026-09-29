import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AnSaoScreen } from "./an-sao-screen";

const { previewData } = vi.hoisted(() => ({
  previewData: { chinh_tinh: ["Tham Lang"] },
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/lib/api/hooks", () => ({
  profileDisplayName: () => "01/01/2000",
  useBuildLaso: () => ({ mutateAsync: vi.fn() }),
  useCreateChartProfile: () => ({ mutateAsync: vi.fn() }),
  useLasoPreview: (birth: { hour?: number } | null) => ({
    data: birth === null ? undefined : previewData,
    isPlaceholderData: birth?.hour === 4,
  }),
}));

describe("AnSaoScreen hierarchy", () => {
  it("puts the primary action before the atmospheric reward in reading order", () => {
    render(<AnSaoScreen />);

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
