// Mirrors backend openapi schema at localhost:8000/openapi.json
export interface StarPayload {
  name: string;
  display: string;
  element: string;
}

export interface CungPayload {
  position: string;
  role: string | null;
  chinh_tinh: string[];
  phu_tinh: StarPayload[];
  tuhoa: string[];
  trang_sinh: string | null;
  is_tuan: boolean;
  is_triet: boolean;
  is_cung_than: boolean;
  age_daivan: number | null;
  saoLuu: StarPayload[];
}

export interface BuildLasoResponse {
  id: string;
  summary: string;
  cung_by_position: Record<string, CungPayload>;
}

export interface BuildLasoRequest {
  day: number;
  month: number;
  year: number;
  hour: number;
  gender: "M" | "F";
}

export type Calendar = "duong" | "am";

export interface UserProfile {
  name: string;
  gender: "M" | "F";
  calendar: Calendar;
  day: number;
  month: number;
  year: number;
  hour: number;
  minute: number;
}

export interface SessionStash {
  laso: BuildLasoResponse;
  profile: UserProfile;
  ownerId?: string;
  chartProfileId?: string;
  sessionId?: string;
  fetchedAt: string; // ISO
}

export type Sender = "ai" | "me";
export type ChatMessageRole = "user" | "assistant";

export interface ChatToolEntry {
  id: string;
  name: string;
  arguments: unknown;
  result?: unknown;
}

export interface ChatMessage {
  id: string;
  sender: Sender;
  body: string; // may contain inline markers: [[ref:Quan Lộc]], [[sao:Kình Dương]]
  toolCalls?: ChatToolEntry[];
  streaming?: boolean;
}

export type OverlayKind = "daiVan" | "lichSu" | null;

export interface ChatToolCall {
  id: string | null;
  name: string;
  arguments: unknown;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  answer: string;
  tool_calls: ChatToolCall[];
}
