import { describe, expect, it } from "vitest";

import { daysInMonth, isRealDate } from "./calendar-date";

describe("daysInMonth", () => {
  it.each([
    [2026, 1, 31],
    [2026, 4, 30],
    [2026, 12, 31],
    [2026, 2, 28],
    [2024, 2, 29],
    [2000, 2, 29],
    [1900, 2, 28],
  ])("%i-%i has %i days", (year, month, days) => {
    expect(daysInMonth(year, month)).toBe(days);
  });
});

describe("isRealDate", () => {
  it("accepts the last day of a month and a leap day", () => {
    expect(isRealDate({ year: 2026, month: 4, day: 30 })).toBe(true);
    expect(isRealDate({ year: 2000, month: 2, day: 29 })).toBe(true);
  });

  it.each([
    { year: 2000, month: 2, day: 31 },
    { year: 2001, month: 2, day: 29 },
    { year: 2026, month: 4, day: 31 },
    { year: 2026, month: 1, day: 0 },
    { year: 2026, month: 13, day: 1 },
  ])("rejects %o", (date) => {
    expect(isRealDate(date)).toBe(false);
  });
});
