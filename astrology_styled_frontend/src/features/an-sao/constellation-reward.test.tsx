import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ConstellationReward } from "./constellation-reward";

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
