import { describe, expect, it } from "vitest";

import type { ChatSessionSummary } from "@/lib/api/schemas";

import { sessionLabel } from "./session-label";

const BASE: ChatSessionSummary = {
  id: "s1",
  chart_profile_id: "p1",
  title: null,
  message_count: 0,
  created_at: "2026-08-29T08:00:00+00:00",
  updated_at: "2026-08-29T08:00:00+00:00",
};

describe("sessionLabel", () => {
  it("returns the stored title when present", () => {
    expect(sessionLabel({ ...BASE, title: "Bàn về công danh" })).toBe("Bàn về công danh");
  });

  it("derives a label from the creation date for an untitled session", () => {
    expect(sessionLabel(BASE)).toBe("Cuộc trò chuyện 29/08");
  });

  it("appends the message count once there are messages", () => {
    expect(sessionLabel({ ...BASE, message_count: 5 })).toBe("Cuộc trò chuyện 29/08 · 5 tin nhắn");
  });
});
