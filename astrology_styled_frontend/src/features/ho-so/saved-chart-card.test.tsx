import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ChartProfile } from "@/lib/api/schemas";
import { ApiErrorException } from "@/lib/http/errors";

import { SavedChartCard, SavedChartSkeleton } from "./saved-chart-card";

const mocks = vi.hoisted(() => ({
  rename: vi.fn(),
  renameHook: vi.fn(),
  remove: vi.fn(),
  reset: vi.fn(),
}));
vi.mock("@/lib/api/hooks", () => ({
  useDeleteChartProfile: () => ({ mutate: mocks.remove, isPending: false }),
  useRenameChartProfile: mocks.renameHook,
}));

const PROFILE: ChartProfile = {
  id: "p1",
  display_name: "Lá số 1",
  birth_info: { calendar: "solar", year: 1996, month: 4, day: 15, hour: 8, gender: "M" },
  created_at: "2026-08-28T00:00:00+00:00",
  updated_at: "2026-08-28T00:00:00+00:00",
};
const RENAME = { mutate: mocks.rename, reset: mocks.reset, isPending: false, isError: false };

beforeEach(() => {
  vi.clearAllMocks();
  mocks.rename.mockReset();
  mocks.renameHook.mockReturnValue(RENAME);
});

describe("SavedChartCard", () => {
  it("shows the full wrapped name, birth date and canh hour without fixed card height", () => {
    const longName = "Gia đình và những người thân yêu ".repeat(4);
    const { container, rerender } = render(
      <SavedChartCard profile={{ ...PROFILE, display_name: longName }} />,
    );
    const heading = screen.getByRole("heading", { name: longName.trim() });
    expect(heading.textContent).toBe(longName);
    expect(heading.className).not.toMatch(/line-clamp|truncate/);
    expect(heading.className).toContain("[overflow-wrap:anywhere]");
    expect(screen.getByRole("article").className).not.toMatch(/\bh-\d/);
    expect(screen.getByRole("article").className).toContain(
      "min-h-[128px] w-full min-w-0 flex-row",
    );
    expect(screen.getByText("Ngày sinh: 15/04/1996")).toBeTruthy();
    expect(screen.getByText("Giờ sinh: Thìn · 07:00 – 09:00")).toBeTruthy();
    expect(screen.getByRole("button", { name: /Đổi tên lá số/ }).className).toContain("min-h-11");
    expect(screen.getByRole("button", { name: /Đổi tên lá số/ }).parentElement?.className).toBe(
      "flex shrink-0 flex-col gap-2",
    );
    rerender(<SavedChartCard profile={PROFILE} />);
    expect(screen.getByRole("heading").textContent).toBe("Lá số 1");
    rerender(<SavedChartSkeleton />);
    expect(container.firstElementChild?.className).toContain(
      "min-h-[128px] w-full min-w-0 flex-row",
    );
    expect(container.firstElementChild?.lastElementChild?.className).toBe("shrink-0 space-y-2");
    expect(container.firstElementChild?.lastElementChild?.children).toHaveLength(2);
  });

  it("trims renames, keeps pending edits open, shows failures and closes after success", () => {
    const { rerender } = render(<SavedChartCard profile={PROFILE} />);
    fireEvent.click(screen.getByRole("button", { name: /Đổi tên lá số/ }));
    const input = screen.getByLabelText("Tên lá số") as HTMLInputElement;
    expect(input.value).toBe("Lá số 1");
    expect(input.maxLength).toBe(80);
    fireEvent.change(input, { target: { value: "  Gia đình  " } });
    fireEvent.click(screen.getByRole("button", { name: "Lưu" }));
    expect(mocks.rename).toHaveBeenCalledWith(
      { id: "p1", display_name: "Gia đình" },
      expect.any(Object),
    );

    mocks.renameHook.mockReturnValue({ ...RENAME, isPending: true });
    rerender(<SavedChartCard profile={PROFILE} />);
    expect((screen.getByRole("button", { name: "Hủy" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.keyDown(screen.getByRole("dialog"), { key: "Escape" });
    expect(screen.getByRole("dialog")).toBeTruthy();

    mocks.renameHook.mockReturnValue({
      ...RENAME,
      isError: true,
      error: new ApiErrorException({ kind: "network" }),
    });
    rerender(<SavedChartCard profile={PROFILE} />);
    expect(screen.getByRole("alert").textContent).toContain("Không kết nối được máy chủ.");
    mocks.renameHook.mockReturnValue(RENAME);
    mocks.rename.mockImplementation((_input: unknown, options: { onSuccess: () => void }) =>
      options.onSuccess(),
    );
    rerender(<SavedChartCard profile={PROFILE} />);
    fireEvent.click(screen.getByRole("button", { name: "Lưu" }));
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("cancels renaming without a write and still requires delete confirmation", () => {
    render(<SavedChartCard profile={PROFILE} />);
    fireEvent.click(screen.getByRole("button", { name: /Đổi tên lá số/ }));
    fireEvent.click(screen.getByRole("button", { name: "Hủy" }));
    expect(mocks.rename).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: /Xoá lá số/ }));
    expect(mocks.remove).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Giữ lại" }));
    expect(screen.queryByRole("dialog")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /Xoá lá số/ }));
    fireEvent.click(screen.getByRole("button", { name: "Xoá" }));
    expect(mocks.remove).toHaveBeenCalledWith(
      "p1",
      expect.objectContaining({ onError: expect.any(Function) }),
    );
  });
});
