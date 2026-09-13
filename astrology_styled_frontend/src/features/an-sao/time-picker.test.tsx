import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MERIDIEM } from "./birth-time";
import { TimePicker } from "./time-picker";

describe("TimePicker", () => {
  it("announces an empty value, then the selected birth hour", () => {
    const onChange = vi.fn();
    const { rerender } = render(
      <TimePicker value={null} meridiem={MERIDIEM.AM} onChange={onChange} pulseKey={0} />,
    );

    const slider = screen.getByRole("slider", { name: "Giờ sinh" });
    expect(slider.getAttribute("aria-valuetext")).toBe("Chưa chọn giờ sinh");
    expect(screen.getByText("Chọn giờ")).toBeTruthy();

    rerender(<TimePicker value={12} meridiem={MERIDIEM.AM} onChange={onChange} pulseKey={1} />);
    expect(slider.getAttribute("aria-valuetext")).toContain("12 giờ AM");
  });
});
