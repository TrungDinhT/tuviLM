import type { CauPhuResponse } from "@/app/_lib/types";
import { API_URL } from "@/constants/env";

export async function getCauPhu(): Promise<CauPhuResponse> {
  const res = await fetch(`${API_URL}/api/v1/laso/cau-phu`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Không lấy được Câu Phú (HTTP ${res.status})`);
  }

  const data: unknown = await res.json();
  if (!isCauPhuResponse(data)) {
    throw new Error("Phản hồi Câu Phú không hợp lệ");
  }
  return data;
}

function isCauPhuResponse(value: unknown): value is CauPhuResponse {
  if (!value || typeof value !== "object") return false;
  const data = value as Record<string, unknown>;
  return (
    typeof data.vi_tri === "string" &&
    Array.isArray(data.chinh_tinh) &&
    data.chinh_tinh.every((star) => typeof star === "string") &&
    typeof data.co_tuan === "boolean" &&
    typeof data.co_triet === "boolean" &&
    typeof data.tuan_triet === "string" &&
    typeof data.tieu_de === "string" &&
    typeof data.cau_phu === "string" &&
    Array.isArray(data.cac_cau) &&
    data.cac_cau.every((line) => typeof line === "string")
  );
}
