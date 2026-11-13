import { expect, it } from "vitest";

import type { BirthInfo, ChartProfile } from "@/lib/api/schemas";

import { birthDetail, findCurrentProfile, normalize } from "./profile-format";

const birth = (year: number): BirthInfo => ({
  calendar: "solar",
  year,
  month: 4,
  day: 15,
  hour: 8,
  gender: "F",
});
const profile = (id: string, year: number): ChartProfile => ({
  id,
  display_name: id,
  birth_info: birth(year),
  created_at: "2026-10-04T00:00:00Z",
  updated_at: "2026-10-04T00:00:00Z",
});

it("finds the profile on screen by id first, then by birth data", () => {
  const saved = [profile("a", 1990), profile("b", 1991)];
  expect(findCurrentProfile(saved, "b", birth(1990))?.id).toBe("b");
  expect(findCurrentProfile(saved, null, birth(1990))?.id).toBe("a");
  expect(findCurrentProfile(saved, "gone", birth(2000))).toBeUndefined();
});

it("matches names without Vietnamese marks or case", () => {
  expect(normalize("  Mẹ Đào ")).toBe("me dao");
});

it("describes the birth hour and gender", () => {
  expect(birthDetail(birth(1990))).toBe("Giờ Thìn · Nữ");
});
