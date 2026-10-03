import { describe, expect, it } from "vitest";

import { canhGioOf, toApiBirthTime } from "./birth-time";

describe("toApiBirthTime", () => {
  it("maps a mid-block time to the canh-giờ midpoint", () => {
    const result = toApiBirthTime(
      { year: 1995, month: 3, day: 15 },
      { hour12: 7, meridiem: "AM" },
    );

    expect(result).toEqual({ ok: true, value: { year: 1995, month: 3, day: 15, hour: 8 } });
  });

  it("rolls an 11 PM pick to hour 0 of the next day (giờ Tý)", () => {
    const result = toApiBirthTime(
      { year: 1995, month: 3, day: 15 },
      { hour12: 11, meridiem: "PM" },
    );

    expect(result).toEqual({ ok: true, value: { year: 1995, month: 3, day: 16, hour: 0 } });
  });

  it("keeps midnight Tý (12 AM) on the same day", () => {
    const result = toApiBirthTime(
      { year: 1995, month: 3, day: 15 },
      { hour12: 12, meridiem: "AM" },
    );

    expect(result).toEqual({ ok: true, value: { year: 1995, month: 3, day: 15, hour: 0 } });
  });

  it("maps noon (12 PM) to giờ Ngọ", () => {
    const result = toApiBirthTime(
      { year: 1995, month: 3, day: 15 },
      { hour12: 12, meridiem: "PM" },
    );

    expect(result).toEqual({ ok: true, value: { year: 1995, month: 3, day: 15, hour: 12 } });
  });

  it("rolls over month and year boundaries", () => {
    const result = toApiBirthTime(
      { year: 2026, month: 12, day: 31 },
      { hour12: 11, meridiem: "PM" },
    );

    expect(result).toEqual({ ok: true, value: { year: 2027, month: 1, day: 1, hour: 0 } });
  });

  it("fails closed when the rollover exceeds the supported year range", () => {
    const result = toApiBirthTime(
      { year: 2099, month: 12, day: 31 },
      { hour12: 11, meridiem: "PM" },
    );

    expect(result).toEqual({ ok: false, reason: "year-overflow" });
  });

  it.each([
    [{ hour12: 1, meridiem: "AM" } as const, 2], // Sửu
    [{ hour12: 3, meridiem: "AM" } as const, 4], // Dần
    [{ hour12: 5, meridiem: "AM" } as const, 6], // Mão
    [{ hour12: 9, meridiem: "AM" } as const, 10], // Tỵ
    [{ hour12: 2, meridiem: "PM" } as const, 14], // Mùi
    [{ hour12: 4, meridiem: "PM" } as const, 16], // Thân
    [{ hour12: 6, meridiem: "PM" } as const, 18], // Dậu
    [{ hour12: 8, meridiem: "PM" } as const, 20], // Tuất
    [{ hour12: 10, meridiem: "PM" } as const, 22], // Hợi
  ])("maps %o to midpoint hour %i", (time, expectedHour) => {
    const result = toApiBirthTime({ year: 2000, month: 6, day: 10 }, time);

    expect(result).toMatchObject({ ok: true, value: { hour: expectedHour } });
  });
});

describe("canhGioOf", () => {
  it("labels the readout with the canh giờ and its range", () => {
    expect(canhGioOf(7, "AM")).toEqual({ chi: "Thìn", range: "07:00 – 09:00" });
    expect(canhGioOf(11, "PM")).toEqual({ chi: "Tý", range: "23:00 – 01:00" });
    expect(canhGioOf(12, "AM")).toEqual({ chi: "Tý", range: "23:00 – 01:00" });
    expect(canhGioOf(12, "PM")).toEqual({ chi: "Ngọ", range: "11:00 – 13:00" });
  });
});
