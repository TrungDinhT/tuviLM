import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MERIDIEM } from "./birth-time";
import { TimePicker } from "./time-picker";

describe("TimePicker", () => {
  it("exposes a clear required empty state, then a selected state", () => {
    const onChange = vi.fn();
    const { rerender } = render(
      <TimePicker value={null} meridiem={MERIDIEM.AM} onChange={onChange} pulseKey={0} />,
    );

    const slider = screen.getByRole("slider", { name: "Giờ sinh bắt buộc" });
    expect(slider.dataset.state).toBe("empty");
    expect(slider.getAttribute("aria-invalid")).toBe("false");
    expect(slider.getAttribute("aria-valuetext")).toBe("Chưa chọn giờ sinh");
    expect(screen.getByText("Chạm số hoặc vuốt")).toBeTruthy();

    rerender(<TimePicker value={null} meridiem={MERIDIEM.AM} onChange={onChange} pulseKey={1} />);
    expect(slider.getAttribute("aria-invalid")).toBe("true");

    rerender(<TimePicker value={12} meridiem={MERIDIEM.AM} onChange={onChange} pulseKey={1} />);
    expect(slider.dataset.state).toBe("selected");
    expect(slider.getAttribute("aria-invalid")).toBe("false");
    expect(slider.getAttribute("aria-valuetext")).toContain("12 giờ AM");
  });
});
