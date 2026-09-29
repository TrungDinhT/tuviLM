import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, within, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import fixture from "@/lib/api/__fixtures__/build-laso.json";
import { queryKeys } from "@/lib/api/queryKeys";
import type { BuildLasoResponse } from "@/lib/api/schemas";
import { useChartStore } from "@/store/chart-store";
import { LaSoBoard, LaSoScreen } from "./la-so-screen";

const chart = fixture as BuildLasoResponse;

beforeEach(() => useChartStore.getState().reset());

describe("full lá số", () => {
  it("places all 12 cung in the traditional grid and opens each one's actual stars", () => {
    render(<LaSoBoard chart={chart} />);
    const board = screen.getByLabelText("12 cung lá số");
    const cells = within(board).getAllByRole("button");
    expect(cells).toHaveLength(12);
    expect(cells[0]!.style.gridRow).toBe("1");
    expect(cells[0]!.style.gridColumn).toBe("1");
    expect(cells[0]!.getAttribute("aria-label")).toContain("Tị");
    expect(cells[7]!.style.gridRow).toBe("4");
    expect(cells[7]!.style.gridColumn).toBe("3");

    for (const cell of cells) {
      fireEvent.click(cell);
      const dialog = screen.getByRole("dialog");
      const cung = Object.values(chart.cung_by_position).find(
        (item) =>
          cell.getAttribute("aria-label") ===
          `Xem cung ${item.role ?? item.position} tại ${item.position}`,
      )!;
      expect(within(dialog).getByRole("heading", { name: `Cung ${cung.role}` })).toBeTruthy();
      for (const star of cung.chinh_tinh) expect(within(dialog).getByText(star)).toBeTruthy();
      for (const star of cung.phu_tinh) expect(within(dialog).getByText(star.display)).toBeTruthy();
      for (const star of cung.tuhoa) expect(within(dialog).getByText(star)).toBeTruthy();
      if (!cung.chinh_tinh.length) expect(within(dialog).getByText("Vô chính diệu")).toBeTruthy();
      expect(within(dialog).queryByText(/Đại vận/)).toBeNull();
      fireEvent.click(within(dialog).getByRole("button", { name: "Đóng chi tiết cung" }));
      expect(screen.queryByRole("dialog")).toBeNull();
    }
  });

  it("previews requested groups, counts omitted stars, and colors their elements", () => {
    render(
      <LaSoBoard
        chart={{
          ...chart,
          cuc_name: "Kim Tứ cục",
          ban_menh_name: "Thành Đầu Thổ",
          ban_menh_ngu_hanh: "Thổ",
        }}
      />,
    );
    const ty = screen.getByRole("button", { name: "Xem cung Huynh Đệ tại Tý" });
    expect(within(ty).getByText("Hóa Quyền").style.color).toBe("var(--element-moc)");
    expect(within(ty).getByText("Hỏa Tinh").style.color).toBe("var(--element-hoa)");
    expect(within(ty).queryByText("Phi Liêm")).toBeNull();
    expect(within(ty).getByText("+3")).toBeTruthy();

    const suu = screen.getByRole("button", { name: "Xem cung Mệnh tại Sửu" });
    expect(within(suu).getByText("Linh Tinh")).toBeTruthy();
    expect(within(suu).queryByText("Hoa Cái")).toBeNull();
    expect(within(suu).getByText("Thái Tuế").style.color).toBe("var(--element-hoa)");
    expect(within(suu).getByText("+3")).toBeTruthy();

    const than = screen.getByRole("button", { name: "Xem cung Tật Ách tại Thân" });
    expect(within(than).getByText("Hữu Bật")).toBeTruthy();

    const thin = screen.getByRole("button", { name: "Xem cung Điền Trạch tại Thìn" });
    expect(within(thin).queryByText("Thanh Long")).toBeNull();
    expect(within(thin).getByText("Thiếu Âm").style.color).toBe("var(--element-thuy)");
    expect(within(thin).getByText("+2")).toBeTruthy();
    expect(screen.getByText("Kim Tứ cục").style.color).toBe("var(--element-kim)");
    expect(screen.getByText("Thành Đầu Thổ").style.color).toBe("var(--element-tho)");

    fireEvent.click(ty);
    const dialog = screen.getByRole("dialog");
    expect(within(dialog).getByText("Phi Liêm").style.color).toBe("var(--element-hoa)");
    expect(within(dialog).getByText("Hóa Quyền").style.color).toBe("var(--element-moc)");
  });

  it("shows age ranges and markers, and restores focus after Escape", async () => {
    const variant: BuildLasoResponse = {
      ...chart,
      cung_by_position: {
        ...chart.cung_by_position,
        Tị: {
          ...chart.cung_by_position["Tị"]!,
          age_daivan: 44,
          is_tuan: true,
          is_triet: true,
          is_cung_than: true,
        },
      },
    };
    render(<LaSoBoard chart={variant} />);
    const cell = screen.getByRole("button", { name: "Xem cung Quan Lộc tại Tị" });
    cell.focus();
    fireEvent.click(cell);
    const dialog = screen.getByRole("dialog");
    expect(within(dialog).getByText(/Đại vận 44–53/)).toBeTruthy();
    expect(within(dialog).getByText("Cung Thân · Tuần · Triệt")).toBeTruthy();
    fireEvent.keyDown(dialog, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(document.activeElement).toBe(cell);
  });

  it("clears palace details when switching or resetting the chart", async () => {
    const client = new QueryClient();
    client.setQueryData(queryKeys.laso.chart(chart.id), chart);
    useChartStore.getState().castChart({ stars: [] }, chart.id);
    render(
      <QueryClientProvider client={client}>
        <LaSoScreen />
      </QueryClientProvider>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Xem cung Quan Lộc tại Tị" }));
    expect(screen.getByRole("dialog")).toBeTruthy();

    const nextChart = { ...chart, id: "another-chart" };
    act(() => {
      client.setQueryData(queryKeys.laso.chart(nextChart.id), nextChart);
      useChartStore.getState().castChart({ stars: [] }, nextChart.id);
    });
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(screen.getByLabelText("12 cung lá số")).toBeTruthy();
    act(() => useChartStore.getState().reset());
    await waitFor(() => expect(screen.queryByLabelText("12 cung lá số")).toBeNull());
  });
});
