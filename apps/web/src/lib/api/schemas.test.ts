import { describe, expect, it } from "vitest";

import fixture from "./__fixtures__/build-laso.json";
import {
  birthInfoSchema,
  buildLasoResponseSchema,
  previewLasoRequestSchema,
  sseChatEventSchema,
} from "./schemas";

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

describe("sseChatEventSchema", () => {
  it.each([
    { type: "ids", user_message_id: "u1", assistant_message_id: "a1" },
    { type: "text", delta: "xin chào" },
    { type: "done", status: "confirmed" },
    { type: "done", status: "duplicate_in_progress" },
    {
      type: "duplicate_in_progress",
      user_message_id: "u1",
      assistant_message_id: "a1",
      status: "pending",
    },
    { type: "tool_call", id: "t1", name: "xem", arguments: { a: 1 } },
    { type: "error", message: "boom" },
  ])("accepts %o", (event) => {
    expect(sseChatEventSchema.parse(event).type).toBe(event.type);
  });

  it("rejects an unknown event type", () => {
    expect(sseChatEventSchema.safeParse({ type: "bogus" }).success).toBe(false);
  });

  it("rejects a text event missing its delta", () => {
    expect(sseChatEventSchema.safeParse({ type: "text" }).success).toBe(false);
  });
});

describe("birth date schemas", () => {
  const birth = { calendar: "solar", year: 2000, month: 2, day: 29, hour: 8, gender: "M" } as const;

  it("accepts a leap day", () => {
    expect(birthInfoSchema.parse(birth).day).toBe(29);
    expect(previewLasoRequestSchema.parse({ ...birth, gender: undefined }).day).toBe(29);
  });

  it.each([
    { year: 2000, day: 31 },
    { year: 2001, day: 29 },
  ])("rejects a date that does not exist: %o", (change) => {
    for (const schema of [birthInfoSchema, previewLasoRequestSchema]) {
      const result = schema.safeParse({ ...birth, ...change });

      expect(result.success).toBe(false);
      expect(result.error?.issues[0]?.path).toEqual(["day"]);
    }
  });
});
