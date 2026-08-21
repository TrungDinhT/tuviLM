import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import fixture from "@/lib/api/__fixtures__/build-laso.json";
import { bindChartResetClearing } from "@/lib/api/chart-persistence";
import { queryKeys } from "@/lib/api/queryKeys";
import type { BuildLasoResponse, Cung } from "@/lib/api/schemas";
import { useChartStore } from "@/store/chart-store";

import { BanMenhScreen } from "./ban-menh-screen";
import { AdviceCard } from "./advice-card";
import { DestinyCard } from "./destiny-card";
import { LuckCard } from "./luck-card";

const chart = fixture as BuildLasoResponse;

function cung(over: Partial<Cung>): Cung {
  return {
    position: "Tý",
    role: null,
    chinh_tinh: [],
    phu_tinh: [],
    tuhoa: [],
    trang_sinh: null,
    is_tuan: false,
    is_triet: false,
    is_cung_than: false,
    age_daivan: null,
    saoLuu: [],
    ...over,
  };
}

/** A chart variant keeping the fixture's foundation fields. */
function chartWith(menhStars: string[]): BuildLasoResponse {
  return {
    ...chart,
    cung_by_position: {
      ...chart.cung_by_position,
      Tý: cung({ position: "Tý", role: "Mệnh", chinh_tinh: menhStars }),
      // The fixture's own Mệnh cung is demoted so only one Mệnh remains.
      Sửu: cung({ position: "Sửu", role: "Huynh Đệ" }),
    },
  };
}

function seedChart(client: QueryClient) {
  client.setQueryData(queryKeys.laso.chart(chart.id), chart);
  useChartStore.getState().castChart({ stars: ["cumon", "thiendong"] }, chart.id);
}

function renderScreen(client: QueryClient) {
  return render(
    <QueryClientProvider client={client}>
      <BanMenhScreen />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  useChartStore.setState({ hasChart: false, outcome: null, previewOutcome: null, chartId: null });
});

describe("BanMenhScreen", () => {
  it("renders the whole deck from the cached chart, with no request issued", async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    const client = new QueryClient();
    seedChart(client);

    renderScreen(client);

    expect(await screen.findByText("TỬ VI CÁ NHÂN")).toBeTruthy();
    expect(screen.getByText("Vận May")).toBeTruthy();
    expect(screen.getByText("Lời Khuyên")).toBeTruthy();
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("clears all deck content when the chart state resets", async () => {
    const client = new QueryClient();
    seedChart(client);
    const unbind = bindChartResetClearing(client);
    renderScreen(client);
    expect(await screen.findByText("TỬ VI CÁ NHÂN")).toBeTruthy();

    act(() => useChartStore.getState().reset());
    unbind();

    expect(screen.queryByText("TỬ VI CÁ NHÂN")).toBeNull();
    expect(screen.queryByText("Vận May")).toBeNull();
  });

  it("renders nothing without a chart", () => {
    const { container } = renderScreen(new QueryClient());
    expect(container.firstChild).toBeNull();
  });
});

describe("deck cards", () => {
  it("no card renders an empty archetype, mantra, blurb, colour, month list, or advice", () => {
    const variants = [
      chart, // the real fixture: song tinh Mệnh
      chartWith(["Tử Vi (Miếu)"]), // single chính tinh with trạng thái suffix
      chartWith(["Thiên Phủ", "Tử Vi"]), // song tinh, reversed order
      chartWith([]), // vô chính diệu
    ];

    for (const variant of variants) {
      const { unmount } = render(
        <QueryClientProvider client={new QueryClient()}>
          <BanMenhScreenHarness chart={variant} />
        </QueryClientProvider>,
      );

      const destiny = document.querySelector(".destiny");
      expect(destiny?.querySelector(".dchip")?.textContent?.trim().length).toBeGreaterThan(1);
      expect(destiny?.querySelector(".dmantra")?.textContent?.trim()).not.toBe("");

      const luck = document.querySelector(".luck-card");
      const luckText = luck?.textContent ?? "";
      expect(luckText).toContain("Hóa Lộc tại");
      expect(luckText).toContain("Lộc Tồn tại");
      expect(luckText).toMatch(/Tháng cát: [\d ·]+ \(âm lịch\)/);
      expect(luck?.querySelector(".luck-orb")).not.toBeNull();

      const advice = document.querySelector(".tarot:not(.luck-card)");
      expect(advice?.querySelector(".key")?.textContent?.trim()).not.toBe("");
      expect(advice?.querySelector("p")?.textContent?.trim()).not.toBe("");

      unmount();
    }
  });

  it("resolves a song tinh pair to the same entry in either order", () => {
    const { unmount } = render(
      <QueryClientProvider client={new QueryClient()}>
        <BanMenhScreenHarness chart={chartWith(["Tử Vi", "Thiên Phủ"])} />
      </QueryClientProvider>,
    );
    const first = document.querySelector(".dchip")?.textContent;
    unmount();

    render(
      <QueryClientProvider client={new QueryClient()}>
        <BanMenhScreenHarness chart={chartWith(["Thiên Phủ", "Tử Vi"])} />
      </QueryClientProvider>,
    );
    expect(document.querySelector(".dchip")?.textContent).toBe(first);
  });

  it("sets --luck-hue on the Vận May card and never writes the global accent", () => {
    document.documentElement.style.removeProperty("--accent");
    render(
      <QueryClientProvider client={new QueryClient()}>
        <BanMenhScreenHarness chart={chart} />
      </QueryClientProvider>,
    );

    const luckCard = document.querySelector(".luck-card") as HTMLElement;
    // The fixture's nạp âm is Tích Lịch Hỏa → Hỏa.
    expect(luckCard.style.getPropertyValue("--luck-hue")).toBe("var(--element-hoa)");
    expect(document.documentElement.style.getPropertyValue("--accent")).toBe("");
  });

  it("labels the lucky colour with its nạp âm provenance", () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <BanMenhScreenHarness chart={chart} />
      </QueryClientProvider>,
    );

    expect(screen.getByText(/Tích Lịch Hỏa/)).toBeTruthy();
    expect(screen.getByText("Đỏ san hô")).toBeTruthy();
  });
});

/** Renders the cards directly from a chart, bypassing the cache wiring. */
function BanMenhScreenHarness({ chart }: { chart: BuildLasoResponse }) {
  // Cards are what vary here; the screen shell is covered by its own tests.
  return (
    <>
      <DestinyCard chart={chart} />
      <LuckCard chart={chart} />
      <AdviceCard chart={chart} />
    </>
  );
}
