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
  chart_profile_id: string;
  session_id: string;
  active_leaf_id: string;
  summary: string;
  cung_by_position: Record<string, CungPayload>;
}

export interface BirthMetadata {
  calendar: "solar" | "lunar";
  date: number;
  month: number;
  year: number;
  hour: number;
  minute: number;
  gender: "M" | "F";
}

export interface BuildLasoRequest extends BirthMetadata {
  client_id: string;
  display_name: string;
}

export type Calendar = "duong" | "am";

export interface UserProfile {
  name: string;
  gender: "M" | "F";
  calendar: Calendar;
  date: number;
  month: number;
  year: number;
  hour: number;
  minute: number;
}

export interface SessionStash {
  laso: BuildLasoResponse;
  profile: UserProfile;
  fetchedAt: string; // ISO
}

export type Sender = "assistant" | "user";

export interface ChatToolEntry {
  id: string;
  name: string;
  arguments: unknown;
  result?: unknown;
}

export interface ChatMessage {
  id: string;
  parent_id?: string | null;
  sender: Sender;
  body: string; // may contain inline markers: [[ref:Quan Lộc]], [[sao:Kình Dương]]
  status?: "pending" | "confirmed" | "streaming" | "failed" | "cancelled" | "deleted";
  toolCalls?: ChatToolEntry[];
  created_at?: string | null;
}

export type OverlayKind = "daiVan" | "lichSu" | null;

export interface ChatToolCall {
  id: string | null;
  name: string;
  arguments: unknown;
}

export interface ChatRequest {
  client_id: string;
  session_id: string;
  parent_id: string;
  content: string;
}

export interface ChatResponse {
  answer: string;
  tool_calls: ChatToolCall[];
}

export interface SessionRef {
  id: string;
  chart_profile_id: string;
  active_leaf_id: string;
}

export interface ChartProfileDTO {
  id: string;
  client_id: string;
  display_name: string;
  birth_metadata: BirthMetadata;
}

export interface SessionDetailResponse {
  session: SessionRef;
  chart_profile: ChartProfileDTO;
  laso: BuildLasoResponse;
  messages: ChatMessage[];
  has_more_before: boolean;
}

export interface SessionSummary {
  session_id: string;
  chart_profile_id: string;
  active_leaf_id: string | null;
  display_name: string;
  birth_year: number | null;
  last_message_preview: string;
  message_count: number;
  updated_at: string | null;
}

export interface SessionListResponse {
  sessions: SessionSummary[];
}
