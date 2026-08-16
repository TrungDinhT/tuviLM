import { describe, expect, it } from "vitest";

import { DEFAULT_ACCENT, resolveAccent } from "./theme";

describe("resolveAccent", () => {
  it("returns the pre-chart default when no chart has been cast", () => {
    expect(resolveAccent(null)).toEqual(DEFAULT_ACCENT);
  });

  it("uses the star colour and its light tint for a single chính tinh", () => {
    expect(resolveAccent({ stars: ["tuvi"] })).toEqual({
      accent: "var(--star-tuvi)",
      accent2: "var(--star-tuvi-light)",
      glow: "var(--star-tuvi-glow)",
    });
  });

  it("uses two distinct star colours for song tinh", () => {
    const accent = resolveAccent({ stars: ["vukhuc", "thamlang"] });
    expect(accent).toEqual({
      accent: "var(--star-vukhuc)",
      accent2: "var(--star-thamlang)",
      glow: "var(--star-vukhuc-glow)",
    });
    expect(accent.accent).not.toEqual(accent.accent2);
  });

  it("falls back to neutral for vô chính diệu", () => {
    expect(resolveAccent({ stars: [] })).toEqual({
      accent: "var(--star-neutral)",
      accent2: "var(--star-neutral-light)",
      glow: "var(--star-neutral-glow)",
    });
  });

  it("falls back to neutral for a chính tinh with no palette entry", () => {
    // Liêm Trinh has portrait art in the design but no assigned hue.
    expect(resolveAccent({ stars: ["liemtrinh"] })).toEqual(resolveAccent({ stars: [] }));
  });

  it("falls back to neutral when only one star of a pair is known", () => {
    expect(resolveAccent({ stars: ["tuvi", "cumon"] })).toEqual(resolveAccent({ stars: [] }));
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
