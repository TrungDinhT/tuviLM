import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import fixture from "@/lib/api/__fixtures__/build-laso.json";
import { useChartStore } from "@/store/chart-store";
import { usePreferencesStore } from "@/store/preferences-store";

import { AnSaoScreen } from "./an-sao-screen";

const { previewData, accountState, build, createProfile, push } = vi.hoisted(() => ({
  previewData: { chinh_tinh: ["Tham Lang"] },
  accountState: {
    data: null as { user: { id: string; name: string } } | null,
    isPending: false,
  },
  build: vi.fn(),
  createProfile: vi.fn(),
  push: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/auth-client", () => ({ authClient: { useSession: () => accountState } }));

vi.mock("@/lib/api/hooks", () => ({
  profileDisplayName: () => "01/01/2000",
  useBuildLaso: () => ({ mutateAsync: build }),
  useCreateChartProfile: () => ({ mutateAsync: createProfile }),
  useLasoPreview: (birth: { hour?: number } | null) => ({
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
  accountState.data = null;
  build.mockResolvedValue(fixture);
  createProfile.mockResolvedValue({ chart_profile: { id: "profile-1" } });
  usePreferencesStore.setState({ muteBirthConfirm: false });
  useChartStore.getState().reset();
});

afterEach(() => vi.unstubAllGlobals());

function spinWheel(label: string, option: string) {
  const wheel = screen.getByRole("listbox", { name: label });
  const index = within(wheel)
    .getAllByRole("option")
    .findIndex((element) => element.textContent === option);
  Object.defineProperty(wheel, "scrollTop", { configurable: true, writable: true, value: index * 46 });
  fireEvent.scroll(wheel);
  act(() => vi.advanceTimersByTime(120));
}

describe("AnSaoScreen hierarchy", () => {
  it("prefills saved birth data without changing it when casting again", async () => {
    vi.useFakeTimers();
    try {
      accountState.data = { user: { id: "account-a", name: "Account A" } };
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
        await act(async () => vi.advanceTimersByTimeAsync(2600));
        expect(build).toHaveBeenLastCalledWith(birth);
        expect(createProfile).toHaveBeenLastCalledWith({
          display_name: "01/01/2000",
          birth_info: birth,
        });
        expect(push).toHaveBeenLastCalledWith("/ban-menh");
        view.unmount();
      }
    } finally {
      vi.useRealTimers();
    }
  });

  it("keeps the day wheel to the days the picked month and year have", async () => {
    vi.useFakeTimers();
    try {
      usePreferencesStore.setState({ muteBirthConfirm: true });
      useChartStore.setState({
        birthInfo: { calendar: "solar", year: 2000, month: 1, day: 31, hour: 8, gender: "M" },
      });
      render(<AnSaoScreen />);
      const days = () => within(screen.getByRole("listbox", { name: "Ngày" }));
      expect(days().getAllByRole("option")).toHaveLength(31);

      spinWheel("Tháng", "02");
      expect(days().getAllByRole("option")).toHaveLength(29);
      expect(days().getByRole("option", { selected: true }).textContent).toBe("29");

      spinWheel("Năm", "2001");
      expect(days().getAllByRole("option")).toHaveLength(28);
      expect(days().getByRole("option", { selected: true }).textContent).toBe("28");

      fireEvent.click(screen.getByRole("button", { name: /Luận giải lá số của tôi/ }));
      await act(async () => vi.advanceTimersByTimeAsync(2600));
      expect(build).toHaveBeenLastCalledWith({
        calendar: "solar",
        year: 2001,
        month: 2,
        day: 28,
        hour: 8,
        gender: "M",
      });
    } finally {
      vi.useRealTimers();
    }
  });

  it("keeps the picked day after the month wheel passes a shorter month", async () => {
    vi.useFakeTimers();
    try {
      usePreferencesStore.setState({ muteBirthConfirm: true });
      useChartStore.setState({
        birthInfo: { calendar: "solar", year: 2000, month: 1, day: 31, hour: 8, gender: "M" },
      });
      render(<AnSaoScreen />);
      const days = () => within(screen.getByRole("listbox", { name: "Ngày" }));

      spinWheel("Tháng", "02");
      expect(days().getByRole("option", { selected: true }).textContent).toBe("29");

      spinWheel("Tháng", "05");
      expect(days().getAllByRole("option")).toHaveLength(31);
      expect(days().getByRole("option", { selected: true }).textContent).toBe("31");

      fireEvent.click(screen.getByRole("button", { name: /Luận giải lá số của tôi/ }));
      await act(async () => vi.advanceTimersByTimeAsync(2600));
      expect(build).toHaveBeenLastCalledWith({
        calendar: "solar",
        year: 2000,
        month: 5,
        day: 31,
        hour: 8,
        gender: "M",
      });
    } finally {
      vi.useRealTimers();
    }
  });

  it("does not auto-save an old account's delayed build after the screen unmounts", async () => {
    vi.useFakeTimers();
    try {
      let resolveBuild!: (value: typeof fixture) => void;
      build.mockImplementation(
        () =>
          new Promise((resolve) => {
            resolveBuild = resolve;
          }),
      );
      accountState.data = { user: { id: "account-a", name: "Account A" } };
      usePreferencesStore.setState({ muteBirthConfirm: true });
      const view = render(<AnSaoScreen />);
      fireEvent.keyDown(screen.getByRole("slider", { name: "Giờ sinh" }), { key: "ArrowRight" });
      fireEvent.click(screen.getByRole("radio", { name: "Nam" }));
      fireEvent.click(screen.getByRole("button", { name: /Luận giải lá số của tôi/ }));
      view.unmount();
      accountState.data = { user: { id: "account-b", name: "Account B" } };
      await act(async () => {
        resolveBuild(fixture);
        await vi.advanceTimersByTimeAsync(2600);
      });
      expect(createProfile).not.toHaveBeenCalled();
      expect(useChartStore.getState().hasChart).toBe(false);
      expect(push).not.toHaveBeenCalled();
    } finally {
      vi.useRealTimers();
    }
  });

  it("does not restore an old chart after its delayed auto-save finishes", async () => {
    vi.useFakeTimers();
    try {
      let resolveProfile!: (value: { chart_profile: { id: string } }) => void;
      createProfile.mockImplementation(
        () =>
          new Promise((resolve) => {
            resolveProfile = resolve;
          }),
      );
      accountState.data = { user: { id: "account-a", name: "Account A" } };
      usePreferencesStore.setState({ muteBirthConfirm: true });
      const view = render(<AnSaoScreen />);
      fireEvent.keyDown(screen.getByRole("slider", { name: "Giờ sinh" }), { key: "ArrowRight" });
      fireEvent.click(screen.getByRole("radio", { name: "Nam" }));
      fireEvent.click(screen.getByRole("button", { name: /Luận giải lá số của tôi/ }));
      await act(async () => {
        await Promise.resolve();
      });
      expect(createProfile).toHaveBeenCalledTimes(1);
      view.unmount();
      await act(async () => {
        resolveProfile({ chart_profile: { id: "profile-a" } });
        await vi.advanceTimersByTimeAsync(2600);
      });
      expect(useChartStore.getState().hasChart).toBe(false);
      expect(useChartStore.getState().chartProfileId).toBeNull();
      expect(push).not.toHaveBeenCalled();
    } finally {
      vi.useRealTimers();
    }
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
