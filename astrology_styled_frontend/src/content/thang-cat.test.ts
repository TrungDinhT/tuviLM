import { describe, expect, it } from "vitest";

import { diaChiSchema } from "@/lib/api/schemas";

import { THANG_CAT, thangCatFor } from "./thang-cat";

/** 0-based index of the enum order Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi. */
const INDEX: Record<string, number> = {
  ty: 0,
  suu: 1,
  dan: 2,
  meo: 3,
  thin: 4,
  ti: 5,
  ngo: 6,
  mui: 7,
  than: 8,
  dau: 9,
  tuat: 10,
  hoi: 11,
};

/** Lunar month of a chi — tháng Giêng is Dần. */
function lunarMonth(chiIndex: number): number {
  return (((chiIndex - 2) % 12) + 12) % 12 + 1;
}

describe("THANG_CAT", () => {
  it("has a row for every địa chi", () => {
    expect(Object.keys(THANG_CAT).sort()).toEqual([...diaChiSchema.options].sort());
  });

  it.each(diaChiSchema.options)("%s matches the ±4 / 13−index definitions", (chi) => {
    const i = INDEX[chi]!;
    const row = thangCatFor(chi);

    const expectedTamHop = [lunarMonth((i + 4) % 12), lunarMonth((i - 4 + 12) % 12)].sort(
      (a, b) => a - b,
    );
    const expectedLucHop = lunarMonth((13 - i) % 12);

    expect([...row.tamHop]).toEqual(expectedTamHop);
    expect(row.lucHop).toBe(expectedLucHop);
  });

  it("lists three distinct months per row, all valid lunar months", () => {
    for (const row of Object.values(THANG_CAT)) {
      const months = [...row.tamHop, row.lucHop];
      expect(new Set(months).size).toBe(3);
      for (const month of months) {
        expect(month).toBeGreaterThanOrEqual(1);
        expect(month).toBeLessThanOrEqual(12);
      }
    }
  });
});
