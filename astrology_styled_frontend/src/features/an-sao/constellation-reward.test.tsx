import { act, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CONSTELLATION_WAVE } from "./constellation-wave";
import { ConstellationReward, GodConstellationArt } from "./constellation-reward";

describe("ConstellationReward", () => {
  it("updates the neutral constellation caption when preview data arrives", () => {
    const { rerender } = render(<ConstellationReward stars={null} names={[]} />);

    const sleeping = screen.getByText("CHÒM SAO MỆNH ĐANG NGỦ").parentElement;
    expect(sleeping?.className).toContain("h-[154px]");

    rerender(<ConstellationReward stars={[]} names={[]} />);

    const awake = screen.getByText("MỆNH VÔ CHÍNH DIỆU · TRỜI RỘNG MỞ").parentElement;
    expect(awake?.className).toContain("h-[154px]");
  });
});

it("restarts the link wave at the configured cycle", () => {
  vi.useFakeTimers();
  try {
    render(
      <GodConstellationArt
        shape={{
          points: [
            [20, 20],
            [40, 40],
          ],
          lines: [[0, 1]],
        }}
        silhouette={{ deity: "Test", fillPaths: [], detailPaths: [], symbolPaths: [] }}
        renderSilhouette={false}
        label="test constellation"
      />,
    );

    const svg = screen.getByRole("img");
    const firstLine = svg.querySelector("line");
    act(() => vi.advanceTimersByTime(CONSTELLATION_WAVE.cycleMs));

    expect(svg.querySelector("line")).not.toBe(firstLine);
  } finally {
    vi.useRealTimers();
  }
});
