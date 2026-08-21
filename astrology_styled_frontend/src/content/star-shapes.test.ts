import { describe, expect, it } from "vitest";

import { STAR_SHAPES } from "./star-shapes";

/** All fourteen chính tinh, as normalised keys (`starKeyFromName`). */
const CHINH_TINH_KEYS = [
  "tuvi",
  "thienphu",
  "thatsat",
  "phaquan",
  "thamlang",
  "thaiduong",
  "thaiam",
  "vukhuc",
  "liemtrinh",
  "thienco",
  "thienluong",
  "thientuong",
  "thiendong",
  "cumon",
] as const;

describe("STAR_SHAPES", () => {
  it("resolves every chính tinh to a shape", () => {
    for (const key of CHINH_TINH_KEYS) {
      expect(STAR_SHAPES[key], `missing shape for ${key}`).toBeDefined();
    }
    expect(Object.keys(STAR_SHAPES).sort()).toEqual([...CHINH_TINH_KEYS].sort());
  });

  it("keeps every shape normalised and every line in range", () => {
    for (const [key, shape] of Object.entries(STAR_SHAPES)) {
      for (const [x, y] of shape.pts) {
        expect(x, `${key} x out of range`).toBeGreaterThanOrEqual(0);
        expect(x, `${key} x out of range`).toBeLessThanOrEqual(1);
        expect(y, `${key} y out of range`).toBeGreaterThanOrEqual(0);
        expect(y, `${key} y out of range`).toBeLessThanOrEqual(1);
      }
      for (const [a, b] of shape.lines) {
        expect(shape.pts[a], `${key} line index ${a}`).toBeDefined();
        expect(shape.pts[b], `${key} line index ${b}`).toBeDefined();
      }
    }
  });
});
