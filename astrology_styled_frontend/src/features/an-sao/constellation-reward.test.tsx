import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ConstellationReward } from "./constellation-reward";

describe("ConstellationReward", () => {
  it("keeps the sleeping prompt compact until preview data arrives", () => {
    const { rerender } = render(<ConstellationReward stars={null} names={[]} />);

    const sleeping = screen.getByText("CHỌN GIỜ SINH ĐỂ ĐÁNH THỨC CHÒM SAO").parentElement;
    expect(sleeping?.dataset.state).toBe("sleeping");
    expect(sleeping?.className).toContain("h-[92px]");

    rerender(<ConstellationReward stars={[]} names={[]} />);

    const awake = screen.getByText("MỆNH VÔ CHÍNH DIỆU · TRỜI RỘNG MỞ").parentElement;
    expect(awake?.dataset.state).toBe("awake");
    expect(awake?.className).toContain("h-[154px]");
  });
});
