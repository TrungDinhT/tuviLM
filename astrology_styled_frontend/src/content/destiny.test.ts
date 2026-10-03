import { describe, expect, it } from "vitest";

import { DESTINY_ENTRIES, VO_CHINH_DIEU_KEY, destinyFor } from "./destiny";

/**
 * The 39 keys a real chart can produce — 1 vô chính diệu, 14 đơn tinh, 24
 * song tinh — as swept from the engine across every (Tử Vi, Mệnh) pair.
 */
const EXPECTED_KEYS = [
  "vochinhdieu",
  "cumon",
  "liemtrinh",
  "phaquan",
  "thaiam",
  "thaiduong",
  "thamlang",
  "thatsat",
  "thienco",
  "thiendong",
  "thienluong",
  "thienphu",
  "thientuong",
  "tuvi",
  "vukhuc",
  "cumon+thaiduong",
  "cumon+thienco",
  "cumon+thiendong",
  "liemtrinh+phaquan",
  "liemtrinh+thamlang",
  "liemtrinh+thatsat",
  "liemtrinh+thienphu",
  "liemtrinh+thientuong",
  "phaquan+tuvi",
  "phaquan+vukhuc",
  "thaiam+thaiduong",
  "thaiam+thienco",
  "thaiam+thiendong",
  "thaiduong+thienluong",
  "thamlang+tuvi",
  "thamlang+vukhuc",
  "thatsat+tuvi",
  "thatsat+vukhuc",
  "thienco+thienluong",
  "thiendong+thienluong",
  "thienphu+tuvi",
  "thienphu+vukhuc",
  "thientuong+tuvi",
  "thientuong+vukhuc",
] as const;

describe("DESTINY_ENTRIES", () => {
  it("covers exactly the 39 possible Mệnh configurations", () => {
    expect(Object.keys(DESTINY_ENTRIES).sort()).toEqual([...EXPECTED_KEYS].sort());
  });

  it("has no empty archetype or mantra anywhere", () => {
    for (const entry of Object.values(DESTINY_ENTRIES)) {
      expect(entry.archetype.trim()).not.toBe("");
      expect(entry.mantra.trim()).not.toBe("");
    }
  });
});

describe("destinyFor", () => {
  it("resolves every expected key to its own entry", () => {
    for (const key of EXPECTED_KEYS) {
      expect(destinyFor(key)).toBe(DESTINY_ENTRIES[key]);
    }
  });

  it("falls back to the vô chính diệu entry for an unknown key", () => {
    expect(destinyFor("sao-la")).toBe(DESTINY_ENTRIES[VO_CHINH_DIEU_KEY]);
  });
});
