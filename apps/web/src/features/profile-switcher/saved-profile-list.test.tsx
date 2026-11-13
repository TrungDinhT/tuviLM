import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

import type { ChartProfile } from "@/lib/api/schemas";

import { SavedProfileList } from "./saved-profile-list";

const mocks = vi.hoisted(() => ({
  mutate: vi.fn(),
  open: vi.fn(),
  opening: vi.fn(),
  list: vi.fn(),
  toast: vi.fn(),
}));
vi.mock("@/lib/toast", () => ({ showToast: mocks.toast }));
vi.mock("@/lib/api/chart-profiles", () => ({
  profileDisplayName: (birth: { year: number }) => `15/04/${birth.year}`,
  openChartProfileMutationOptions: () => ({}),
}));
vi.mock("@/lib/api/hooks", () => ({ useChartProfiles: mocks.list }));
vi.mock("@tanstack/react-query", () => ({
  useMutation: mocks.open,
  useIsMutating: () => (mocks.opening() ? 1 : 0),
}));

const IDLE = { mutate: mocks.mutate, isPending: false, isError: false };
const profiles: ChartProfile[] = [
  "Bố",
  "Mẹ Mai",
  "Anh Hai",
  "Chị Ba",
  "Em Út",
  "Bà Nội",
  "Ông",
].map((display_name, index) => ({
  id: `p${index + 1}`,
  display_name,
  birth_info: { calendar: "solar", year: 1960 + index, month: 4, day: 15, hour: 8, gender: "M" },
  created_at: "2026-10-04T00:00:00Z",
  updated_at: "2026-10-04T00:00:00Z",
}));
const names = () => screen.queryAllByRole("button").map((row) => row.textContent);

function renderList(props: Partial<Parameters<typeof SavedProfileList>[0]> = {}) {
  const onSwitched = vi.fn();
  const onSearchChange = vi.fn();
  const view = render(
    <SavedProfileList
      currentId="p1"
      search=""
      onSearchChange={onSearchChange}
      onSwitched={onSwitched}
      {...props}
    />,
  );
  return { ...view, onSwitched, onSearchChange };
}

beforeEach(() => {
  vi.clearAllMocks();
  mocks.open.mockReturnValue(IDLE);
  mocks.opening.mockReturnValue(false);
  mocks.list.mockReturnValue({
    data: { chart_profiles: profiles },
    isPending: false,
    isError: false,
  });
});

it("lists the saved charts without the one on screen", () => {
  renderList();
  expect(names()).toHaveLength(6);
  expect(screen.queryByText("Bố")).toBeNull();
});

it("filters by name or birth date and reports the typed filter", () => {
  const { onSearchChange, rerender, onSwitched } = renderList({ search: "me mai" });
  expect(names()).toEqual([expect.stringContaining("Mẹ Mai")]);
  fireEvent.change(screen.getByRole("searchbox", { name: "Tìm lá số đã lưu" }), {
    target: { value: "1962" },
  });
  expect(onSearchChange).toHaveBeenCalledWith("1962");
  rerender(
    <SavedProfileList
      currentId="p1"
      search="1962"
      onSearchChange={onSearchChange}
      onSwitched={onSwitched}
    />,
  );
  expect(names()).toEqual([expect.stringContaining("Anh Hai")]);
});

it("opens the picked chart, then closes the panel and confirms with a toast", () => {
  const { onSwitched } = renderList();
  fireEvent.click(screen.getByRole("button", { name: /Mẹ Mai/ }));
  const [profile, callbacks] = mocks.mutate.mock.calls[0]!;
  expect(profile).toBe(profiles[1]);
  expect(onSwitched).not.toHaveBeenCalled();
  act(() => callbacks.onSuccess());
  expect(onSwitched).toHaveBeenCalledTimes(1);
  expect(mocks.toast).toHaveBeenCalledWith("Đang xem lá số Mẹ Mai ✦");
});

it("locks every row while a chart is being opened and marks the pending one", () => {
  mocks.opening.mockReturnValue(true);
  mocks.open.mockReturnValue({ ...IDLE, isPending: true, variables: profiles[2] });
  renderList();
  const rows = screen.getAllByRole("button") as HTMLButtonElement[];
  expect(rows.every((row) => row.disabled)).toBe(true);
  expect(screen.getByRole("status").textContent).toBe("Đang mở…");
  expect(screen.getByRole("button", { name: /Anh Hai/ }).textContent).toContain("Đang mở…");
});

it("shows why a chart could not be opened", () => {
  mocks.open.mockReturnValue({ ...IDLE, isError: true, error: new Error("down") });
  renderList();
  expect(screen.getByRole("alert").textContent).toBe("Không mở được lá số. Bạn thử lại nhé.");
});
