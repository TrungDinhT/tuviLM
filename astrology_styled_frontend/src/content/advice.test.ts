import { describe, expect, it } from "vitest";

import { amDuongRelationSchema, menhCucRelationSchema } from "@/lib/api/schemas";

import { ADVICE_ENTRIES, adviceFor } from "./advice";

describe("ADVICE_ENTRIES", () => {
  it("resolves all ten relation × polarity pairs", () => {
    for (const relation of menhCucRelationSchema.options) {
      for (const polarity of amDuongRelationSchema.options) {
        const entry = adviceFor(relation, polarity);
        expect(entry.phrase.trim()).not.toBe("");
        expect(entry.advice.trim()).not.toBe("");
      }
    }
    expect(Object.keys(ADVICE_ENTRIES)).toHaveLength(10);
  });
});
