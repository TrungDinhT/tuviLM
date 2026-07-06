import { API_URL } from "@/constants/env";
import type { BuildLasoRequest } from "@/app/_lib/types";

export interface CreateAnonymousResponse {
  owner_id: string;
}

export interface BirthInfoPayload extends BuildLasoRequest {
  calendar?: "solar";
}

export interface ChartProfilePayload {
  id: string;
  display_name: string;
  birth_info: BirthInfoPayload;
  created_at: string;
  updated_at: string;
}

export interface CreateChartProfileResponse {
  chart_profile: ChartProfilePayload;
}

export interface ListChartProfilesResponse {
  chart_profiles: ChartProfilePayload[];
}

export interface ChatSessionPayload {
  id: string;
  chart_profile_id: string;
  title: string | null;
  messages: ChatMessagePayload[];
  created_at: string;
  updated_at: string;
}

export interface CreateSessionResponse {
  session: ChatSessionPayload;
}

export interface ChatMessagePayload {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: "pending" | "confirmed" | "failed" | "cancelled";
  created_at: string;
  updated_at: string;
}

export interface ChatSessionSummaryPayload {
  id: string;
  chart_profile_id: string;
  title: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ListSessionsResponse {
  sessions: ChatSessionSummaryPayload[];
}

export interface GetSessionResponse {
  session: ChatSessionPayload;
}

export async function createAnonymousOwner(): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/anonymous`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Không tạo được định danh ẩn danh (HTTP ${res.status})`);
  }

  const data = (await res.json()) as CreateAnonymousResponse;
  if (!data.owner_id) {
    throw new Error("Phản hồi định danh ẩn danh không hợp lệ");
  }
  return data.owner_id;
}

export async function createChartProfile({
  ownerId,
  idempotencyKey,
  displayName,
  birthInfo,
}: {
  ownerId: string;
  idempotencyKey: string;
  displayName: string;
  birthInfo: BuildLasoRequest;
}): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/chart-profiles`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "X-Anonymous-Owner-Id": ownerId,
      "Idempotency-Key": idempotencyKey,
    },
    body: JSON.stringify({
      display_name: displayName,
      birth_info: { calendar: "solar", ...birthInfo },
    }),
  });
  if (!res.ok) {
    throw new Error(`Không lưu được hồ sơ lá số (HTTP ${res.status})`);
  }

  const data = (await res.json()) as CreateChartProfileResponse;
  if (!data.chart_profile?.id) {
    throw new Error("Phản hồi hồ sơ lá số không hợp lệ");
  }
  return data.chart_profile.id;
}

export async function listChartProfiles({
  ownerId,
}: {
  ownerId: string;
}): Promise<ChartProfilePayload[]> {
  const res = await fetch(`${API_URL}/api/v1/chart-profiles`, {
    method: "GET",
    headers: {
      "X-Anonymous-Owner-Id": ownerId,
    },
  });
  if (!res.ok) {
    throw new Error(`Không tải được hồ sơ lá số (HTTP ${res.status})`);
  }

  const data = (await res.json()) as ListChartProfilesResponse;
  return data.chart_profiles ?? [];
}

export async function deleteChartProfile({
  ownerId,
  chartProfileId,
}: {
  ownerId: string;
  chartProfileId: string;
}): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/chart-profiles/${encodeURIComponent(chartProfileId)}`, {
    method: "DELETE",
    headers: {
      "X-Anonymous-Owner-Id": ownerId,
    },
  });
  if (!res.ok) {
    throw new Error(`Không xoá được hồ sơ lá số (HTTP ${res.status})`);
  }
}

export async function createChatSession({
  ownerId,
  chartProfileId,
  idempotencyKey,
  title,
}: {
  ownerId: string;
  chartProfileId: string;
  idempotencyKey: string;
  title?: string;
}): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/chart-profiles/${encodeURIComponent(chartProfileId)}/sessions`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "X-Anonymous-Owner-Id": ownerId,
      "Idempotency-Key": idempotencyKey,
    },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) {
    throw new Error(`Không tạo được phiên trò chuyện (HTTP ${res.status})`);
  }

  const data = (await res.json()) as CreateSessionResponse;
  if (!data.session?.id) {
    throw new Error("Phản hồi phiên trò chuyện không hợp lệ");
  }
  return data.session.id;
}

export async function listChatSessions({
  ownerId,
  chartProfileId,
}: {
  ownerId: string;
  chartProfileId: string;
}): Promise<ChatSessionSummaryPayload[]> {
  const res = await fetch(`${API_URL}/api/v1/chart-profiles/${encodeURIComponent(chartProfileId)}/sessions`, {
    method: "GET",
    headers: {
      "X-Anonymous-Owner-Id": ownerId,
    },
  });
  if (!res.ok) {
    throw new Error(`Không tải được lịch sử phiên (HTTP ${res.status})`);
  }

  const data = (await res.json()) as ListSessionsResponse;
  return data.sessions ?? [];
}

export async function getChatSession({
  ownerId,
  sessionId,
}: {
  ownerId: string;
  sessionId: string;
}): Promise<ChatSessionPayload> {
  const res = await fetch(`${API_URL}/api/v1/sessions/${encodeURIComponent(sessionId)}`, {
    method: "GET",
    headers: {
      "X-Anonymous-Owner-Id": ownerId,
    },
  });
  if (!res.ok) {
    throw new Error(`Không tải được phiên trò chuyện (HTTP ${res.status})`);
  }

  const data = (await res.json()) as GetSessionResponse;
  if (!data.session?.id) {
    throw new Error("Phản hồi phiên trò chuyện không hợp lệ");
  }
  return data.session;
}

export async function deleteChatSession({
  ownerId,
  sessionId,
}: {
  ownerId: string;
  sessionId: string;
}): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/sessions/${encodeURIComponent(sessionId)}`, {
    method: "DELETE",
    headers: {
      "X-Anonymous-Owner-Id": ownerId,
    },
  });
  if (!res.ok) {
    throw new Error(`Không xoá được phiên trò chuyện (HTTP ${res.status})`);
  }
}
