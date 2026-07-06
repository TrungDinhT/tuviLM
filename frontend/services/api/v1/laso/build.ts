import { useMutation } from "@tanstack/react-query";
import type {
  BuildLasoRequest,
  BuildLasoResponse,
  BuildSaoLuuRequest,
  BuildSaoLuuResponse,
} from "@/app/_lib/types";
import { API_URL } from "@/constants/env";

export async function buildLaso(req: BuildLasoRequest): Promise<BuildLasoResponse> {
  const res = await fetch(`${API_URL}/api/v1/laso/build`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    throw new Error(`Không lập được lá số (HTTP ${res.status})`);
  }
  const data = await res.json();
  if (!data || typeof data.id !== "string" || !data.cung_by_position) {
    throw new Error("Phản hồi lá số không hợp lệ");
  }
  return data as BuildLasoResponse;
}

export function useBuildLaso() {
  return useMutation({
    mutationFn: buildLaso,
  });
}

export async function buildSaoLuu(req: BuildSaoLuuRequest): Promise<BuildSaoLuuResponse> {
  const res = await fetch(`${API_URL}/api/v1/laso/build_sao_luu`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    throw new Error(`Không lập được sao lưu (HTTP ${res.status})`);
  }
  const data = await res.json();
  if (!data || !data.cung_by_position) {
    throw new Error("Phản hồi sao lưu không hợp lệ");
  }
  return data as BuildSaoLuuResponse;
}
