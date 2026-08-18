import { useQuery } from "@tanstack/react-query";

import type {
  BuildLasoRequest,
  StrengthWeaknessResponse,
} from "@/app/_lib/types";
import { API_URL } from "@/constants/env";

export async function analyzeStrengthWeakness(
  req: BuildLasoRequest,
): Promise<StrengthWeaknessResponse> {
  const res = await fetch(`${API_URL}/api/v1/laso/strength-weakness`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const body: unknown = await res.json().catch(() => null);
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String(body.detail)
        : `HTTP ${res.status}`;
    throw new Error(`Không luận được điểm mạnh và điểm yếu (${detail})`);
  }

  const data: unknown = await res.json();
  if (
    !data ||
    typeof data !== "object" ||
    !("tong_quan" in data) ||
    !("diem_manh" in data) ||
    !("diem_yeu" in data) ||
    typeof data.tong_quan !== "string" ||
    !Array.isArray(data.diem_manh) ||
    !Array.isArray(data.diem_yeu)
  ) {
    throw new Error("Phản hồi luận năng lực không hợp lệ");
  }
  return data as StrengthWeaknessResponse;
}

export function useStrengthWeakness(req: BuildLasoRequest) {
  return useQuery({
    queryKey: ["laso", "strength-weakness", req],
    queryFn: () => analyzeStrengthWeakness(req),
    enabled: false,
    staleTime: Number.POSITIVE_INFINITY,
    gcTime: 30 * 60 * 1000,
    retry: false,
  });
}
