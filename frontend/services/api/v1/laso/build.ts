import { useMutation } from "@tanstack/react-query";
import type { BuildLasoRequest, BuildLasoResponse } from "@/app/_lib/types";
import { API_URL } from "@/constants/env";

export async function buildLaso(req: BuildLasoRequest): Promise<BuildLasoResponse> {
  const res = await fetch(`${API_URL}/api/v1/laso/build`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = typeof body?.detail === "string" ? body.detail : "";
    } catch {
      detail = "";
    }
    throw new Error(detail || `Không lập được lá số (HTTP ${res.status})`);
  }
  const data = await res.json();
  if (
    !data ||
    typeof data.id !== "string" ||
    typeof data.session_id !== "string" ||
    typeof data.active_leaf_id !== "string" ||
    !data.cung_by_position
  ) {
    throw new Error("Phản hồi lá số không hợp lệ");
  }
  return data as BuildLasoResponse;
}

export function useBuildLaso() {
  return useMutation({
    mutationFn: buildLaso,
  });
}
