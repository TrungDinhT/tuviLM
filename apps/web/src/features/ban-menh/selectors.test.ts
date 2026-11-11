import { describe, expect, it } from "vitest";

import type { BuildLasoResponse, Cung } from "@/lib/api/schemas";

import { VO_CHINH_DIEU_KEY, cungRoleHolding, menhChinhTinh, menhStarKey } from "./selectors";

function cung(role: string | null, over: Partial<Cung> = {}): Cung {
  return {
    position: "Tý",
    role,
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

function chartWith(menh: Cung, others: Cung[] = []): BuildLasoResponse {
  const cungs = [menh, ...others];
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
    cung_by_position: Object.fromEntries(cungs.map((c, i) => [`Cung ${i}`, c])),
  };
}

describe("menhStarKey", () => {
  it("keys a single chính tinh", () => {
    expect(menhStarKey(chartWith(cung("Mệnh", { chinh_tinh: ["Tử Vi"] })))).toBe("tuvi");
  });

  it("strips the trạng thái suffix before keying", () => {
    expect(menhStarKey(chartWith(cung("Mệnh", { chinh_tinh: ["Tử Vi (Miếu)"] })))).toBe("tuvi");
  });

  it("keys a song tinh pair the same in either order", () => {
    const a = chartWith(cung("Mệnh", { chinh_tinh: ["Tử Vi (Miếu)", "Thiên Phủ (Đắc)"] }));
    const b = chartWith(cung("Mệnh", { chinh_tinh: ["Thiên Phủ", "Tử Vi"] }));

    expect(menhStarKey(a)).toBe("thienphu+tuvi");
    expect(menhStarKey(b)).toBe(menhStarKey(a));
  });

  it("keys an empty Mệnh to the vô chính diệu entry", () => {
    expect(menhStarKey(chartWith(cung("Mệnh")))).toBe(VO_CHINH_DIEU_KEY);
  });
});

describe("menhChinhTinh", () => {
  it("returns the names as the backend sent them", () => {
    expect(menhChinhTinh(chartWith(cung("Mệnh", { chinh_tinh: ["Cự Môn (Hãm)"] })))).toEqual([
      "Cự Môn (Hãm)",
    ]);
  });

  it("is empty when no cung plays the Mệnh role", () => {
    expect(menhChinhTinh(chartWith(cung(null)))).toEqual([]);
  });
});

describe("cungRoleHolding", () => {
  it("finds Hóa Lộc in tuhoa", () => {
    const chart = chartWith(cung("Mệnh"), [cung("Phụ Mẫu", { tuhoa: ["Hóa Lộc"] })]);

    expect(cungRoleHolding(chart, "Hóa Lộc")).toBe("Phụ Mẫu");
  });

  it("finds Lộc Tồn in phu_tinh", () => {
    const chart = chartWith(cung("Mệnh"), [
      cung("Nô Bộc", {
        phu_tinh: [{ name: "Lộc Tồn", display: "Lộc Tồn", element: "Thổ" }],
      }),
    ]);

    expect(cungRoleHolding(chart, "Lộc Tồn")).toBe("Nô Bộc");
  });

  it("is null when the star is absent", () => {
    expect(cungRoleHolding(chartWith(cung("Mệnh")), "Hóa Lộc")).toBeNull();
  });
});
