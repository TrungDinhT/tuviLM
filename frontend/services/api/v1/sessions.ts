import { API_URL } from "@/constants/env";
import type { SessionDetailResponse, SessionListResponse } from "@/app/_lib/types";

export async function getSessionDetail(
  clientId: string,
  sessionId: string,
): Promise<SessionDetailResponse> {
  const params = new URLSearchParams({ client_id: clientId });
  const res = await fetch(`${API_URL}/api/v1/sessions/${sessionId}?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`Không mở được phiên (HTTP ${res.status})`);
  }
  return await res.json() as SessionDetailResponse;
}

export async function listSessions(clientId: string): Promise<SessionListResponse> {
  const params = new URLSearchParams({ client_id: clientId });
  const res = await fetch(`${API_URL}/api/v1/sessions?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`Không tải được lịch sử (HTTP ${res.status})`);
  }
  return await res.json() as SessionListResponse;
}
