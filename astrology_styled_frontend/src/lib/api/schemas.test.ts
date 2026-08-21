import { describe, expect, it } from "vitest";

import fixture from "./__fixtures__/build-laso.json";
import { buildLasoResponseSchema } from "./schemas";

const FOUNDATION_FIELDS = [
  "menh_cuc_relation",
  "am_duong_relation",
  "dia_chi_natal_year",
  "ban_menh_ngu_hanh",
] as const;

describe("buildLasoResponseSchema", () => {
  it("parses a real backend response and exposes the foundation fields", () => {
    const result = buildLasoResponseSchema.parse(fixture);

    expect(result.menh_cuc_relation).toBe("khac_nhap");
    expect(result.am_duong_relation).toBe("thuan_ly");
    expect(result.dia_chi_natal_year).toBe("suu");
    expect(result.ban_menh_ngu_hanh).toBe("Hỏa");
  });

  it.each(FOUNDATION_FIELDS)("rejects a payload missing %s", (field) => {
    const payload = { ...fixture } as Record<string, unknown>;
    delete payload[field];

    const result = buildLasoResponseSchema.safeParse(payload);

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues.some((issue) => issue.path.includes(field))).toBe(true);
    }
  });

  it("rejects a foundation value outside its enum", () => {
    const result = buildLasoResponseSchema.safeParse({
      ...fixture,
      menh_cuc_relation: "hoa_kim",
    });

    expect(result.success).toBe(false);
  });
});
