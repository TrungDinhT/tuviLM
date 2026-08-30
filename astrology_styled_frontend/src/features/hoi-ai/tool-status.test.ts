import { describe, expect, it } from "vitest";

import { toolStatusLabel } from "./tool-status";

describe("toolStatusLabel", () => {
  it("maps a known workflow tool to a Vietnamese activity label", () => {
    expect(toolStatusLabel("run_tinh_cach_workflow")).toBe("Đang chạy workflow tính cách");
    expect(toolStatusLabel("get_list_cach_cuc")).toBe("Đang tra cứu cách cục");
    expect(toolStatusLabel("get_cung_by_role")).toBe("Đang xem cung");
  });

  it("falls back to a generic label for an unknown tool", () => {
    expect(toolStatusLabel("some_future_tool")).toBe("Đang tra cứu");
  });
});
