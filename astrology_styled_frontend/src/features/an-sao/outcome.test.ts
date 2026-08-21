import { describe, expect, it } from "vitest";

import type { BuildLasoResponse } from "@/lib/api/schemas";

import { outcomeFromChart } from "./outcome";

function chartWith(cung: { position: string; role: string | null; chinh_tinh: string[] }[]): BuildLasoResponse {
  return {
    id: "1996041510M",
    summary: "",
    ban_menh_name: "",
    cuc_name: "",
    menh_cuc_relation_label: "",
    menh_cuc_relation: "binh_hoa",
    am_duong_relation: "thuan_ly",
    dia_chi_natal_year: "ty",
    ban_menh_ngu_hanh: "Kim",
    cung_by_position: Object.fromEntries(
      cung.map((entry) => [
        entry.position,
        {
          position: entry.position,
          role: entry.role,
          chinh_tinh: entry.chinh_tinh,
          phu_tinh: [],
          tuhoa: [],
          trang_sinh: null,
          is_tuan: false,
          is_triet: false,
          is_cung_than: false,
          age_daivan: null,
          saoLuu: [],
        },
      ]),
    ),
  };
}

describe("outcomeFromChart", () => {
  it("reads the chính tinh of cung Mệnh, suffix stripped", () => {
    const chart = chartWith([
      { position: "Tý", role: "Huynh Đệ", chinh_tinh: [] },
      { position: "Tuất", role: "Mệnh", chinh_tinh: ["Thái Dương (Miếu)"] },
    ]);

    expect(outcomeFromChart(chart)).toEqual({ stars: ["thaiduong"] });
  });

  it("keeps both stars of a song tinh Mệnh, in order", () => {
    const chart = chartWith([
      { position: "Tý", role: "Mệnh", chinh_tinh: ["Tử Vi (Miếu)", "Thiên Phủ (Hãm)"] },
    ]);

    expect(outcomeFromChart(chart)).toEqual({ stars: ["tuvi", "thienphu"] });
  });

  it("maps a Mệnh without chính tinh to vô chính diệu", () => {
    const chart = chartWith([{ position: "Dậu", role: "Mệnh", chinh_tinh: [] }]);

    expect(outcomeFromChart(chart)).toEqual({ stars: [] });
  });
});
