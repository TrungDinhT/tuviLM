import { Result, Schema } from "effect";
import { describe, expect, it } from "vitest";

import { validate } from "@/lib/schema";

import fixture from "./__fixtures__/build-laso.json";
import { buildLasoResponseSchema, sseChatEventSchema } from "./schemas";

const FOUNDATION_FIELDS = [
  "menh_cuc_relation",
  "am_duong_relation",
  "dia_chi_natal_year",
  "ban_menh_ngu_hanh",
] as const;

describe("buildLasoResponseSchema", () => {
  it("parses a real backend response and exposes the foundation fields", () => {
    const result = Schema.decodeUnknownSync(buildLasoResponseSchema)(fixture);

    expect(result.menh_cuc_relation).toBe("khac_nhap");
    expect(result.am_duong_relation).toBe("thuan_ly");
    expect(result.dia_chi_natal_year).toBe("suu");
    expect(result.ban_menh_ngu_hanh).toBe("Hỏa");
  });

  it.each(FOUNDATION_FIELDS)("rejects a payload missing %s", (field) => {
    const payload = { ...fixture } as Record<string, unknown>;
    delete payload[field];

    const result = validate(buildLasoResponseSchema, payload);

    expect(Result.isFailure(result)).toBe(true);
    if (Result.isFailure(result)) {
      expect(result.failure.some((issue) => issue.path?.includes(field))).toBe(true);
    }
  });

  it("rejects a foundation value outside its enum", () => {
    const isChart = Schema.is(buildLasoResponseSchema);

    expect(isChart({ ...fixture, menh_cuc_relation: "hoa_kim" })).toBe(false);
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
    expect(Schema.decodeUnknownSync(sseChatEventSchema)(event).type).toBe(event.type);
  });

  it("rejects an unknown event type", () => {
    expect(Schema.is(sseChatEventSchema)({ type: "bogus" })).toBe(false);
  });

  it("rejects a text event missing its delta", () => {
    expect(Schema.is(sseChatEventSchema)({ type: "text" })).toBe(false);
  });
});
