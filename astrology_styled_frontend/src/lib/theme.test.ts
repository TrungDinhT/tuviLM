import { describe, expect, it } from "vitest";

import { DEFAULT_ACCENT, nguHanhOf, resolveAccent, starKeyFromName } from "./theme";

describe("resolveAccent", () => {
  it("returns the pre-chart default when no chart has been cast", () => {
    expect(resolveAccent(null)).toEqual(DEFAULT_ACCENT);
  });

  it("uses the element colour and its light tint for a single chính tinh", () => {
    // Thất Sát thuộc Kim.
    expect(resolveAccent({ stars: ["thatsat"] })).toEqual({
      accent: "var(--element-kim)",
      accent2: "var(--element-kim-light)",
      glow: "var(--element-kim-glow)",
    });
  });

  it("uses the two element colours for song tinh", () => {
    // Vũ Khúc thuộc Kim, Tham Lang thuộc Mộc.
    const accent = resolveAccent({ stars: ["vukhuc", "thamlang"] });
    expect(accent).toEqual({
      accent: "var(--element-kim)",
      accent2: "var(--element-moc)",
      glow: "var(--element-kim-glow)",
    });
    expect(accent.accent).not.toEqual(accent.accent2);
  });

  it("allows a song tinh pair sharing one element", () => {
    // Tử Vi và Thiên Phủ cùng thuộc Thổ.
    expect(resolveAccent({ stars: ["tuvi", "thienphu"] })).toEqual({
      accent: "var(--element-tho)",
      accent2: "var(--element-tho)",
      glow: "var(--element-tho-glow)",
    });
  });

  it("falls back to neutral for vô chính diệu", () => {
    expect(resolveAccent({ stars: [] })).toEqual({
      accent: "var(--accent-neutral)",
      accent2: "var(--accent-neutral-light)",
      glow: "var(--accent-neutral-glow)",
    });
  });

  it("falls back to neutral for an unrecognised star", () => {
    expect(resolveAccent({ stars: ["saola"] })).toEqual(resolveAccent({ stars: [] }));
  });

  it("falls back to neutral when one star of a pair is unrecognised", () => {
    expect(resolveAccent({ stars: ["tuvi", "saola"] })).toEqual(
      resolveAccent({ stars: [] }),
    );
  });

  it("never returns a raw colour value", () => {
    const outcomes = [null, { stars: [] }, { stars: ["tuvi"] }, { stars: ["tuvi", "thienphu"] }];
    for (const outcome of outcomes) {
      const accent = resolveAccent(outcome);
      for (const value of Object.values(accent)) {
        expect(value).toMatch(/^var\(--[a-z0-9-]+\)$/);
      }
    }
  });
});

describe("starKeyFromName", () => {
  it("normalises display names to content keys", () => {
    expect(starKeyFromName("Tử Vi")).toBe("tuvi");
    expect(starKeyFromName("Thái Dương")).toBe("thaiduong");
    expect(starKeyFromName("Thiên Đồng")).toBe("thiendong");
    expect(starKeyFromName("Vũ Khúc")).toBe("vukhuc");
    expect(starKeyFromName("Cự Môn")).toBe("cumon");
  });

  it("strips the trạng thái suffix the build payload carries", () => {
    expect(starKeyFromName("Tử Vi (Miếu)")).toBe("tuvi");
    expect(starKeyFromName("Thất Sát (V)")).toBe("thatsat");
  });
});

describe("nguHanhOf", () => {
  it("maps a chính tinh key to its ngũ hành", () => {
    expect(nguHanhOf("thatsat")).toBe("kim");
    expect(nguHanhOf("thamlang")).toBe("moc");
    expect(nguHanhOf("tuvi")).toBe("tho");
  });

  it("returns null for an unrecognised key", () => {
    expect(nguHanhOf("saola")).toBeNull();
  });
});
