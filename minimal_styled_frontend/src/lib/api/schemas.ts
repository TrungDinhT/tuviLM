import { z } from 'zod';

export const GenderSchema = z.enum(['M', 'F']);
export type Gender = z.infer<typeof GenderSchema>;

export const TuviTimeSchema = z.object({
  day: z.number().int().min(1).max(31),
  month: z.number().int().min(1).max(12),
  year: z.number().int().min(1900).max(2099),
  hour: z.number().int().min(0).max(23),
  gender: GenderSchema,
});
export type TuviTime = z.infer<typeof TuviTimeSchema>;

export const BuildLasoRequestSchema = TuviTimeSchema;
export type BuildLasoRequest = z.infer<typeof BuildLasoRequestSchema>;

export const BuildSaoLuuRequestSchema = z.object({
  observation_time: TuviTimeSchema,
});
export type BuildSaoLuuRequest = z.infer<typeof BuildSaoLuuRequestSchema>;

export const StarSchema = z.object({
  name: z.string(),
  display: z.string(),
  element: z.string(),
  sao_type: z.array(z.string()).optional(),
});
export type Star = z.infer<typeof StarSchema>;

export const CungSchema = z.object({
  position: z.string(),
  role: z.string().nullable().optional(),
  chinh_tinh: z.array(z.string()),
  phu_tinh: z.array(StarSchema),
  tuhoa: z.array(StarSchema),
  trang_sinh: z.string().nullable().optional(),
  is_tuan: z.boolean(),
  is_triet: z.boolean(),
  is_cung_than: z.boolean(),
  age_daivan: z.number().int().nullable().optional(),
  saoLuu: z.array(StarSchema),
});
export type Cung = z.infer<typeof CungSchema>;

export const BuildLasoResponseSchema = z.object({
  id: z.string(),
  summary: z.string(),
  ban_menh_name: z.string(),
  cuc_name: z.string(),
  menh_cuc_relation_label: z.string(),
  cung_by_position: z.record(z.string(), CungSchema),
});
export type BuildLasoResponse = z.infer<typeof BuildLasoResponseSchema>;

export const BuildSaoLuuResponseSchema = z.object({
  cung_by_position: z.record(z.string(), CungSchema),
});
export type BuildSaoLuuResponse = z.infer<typeof BuildSaoLuuResponseSchema>;

export const CreateAnonymousResponseSchema = z.object({
  owner_id: z.string(),
});
export type CreateAnonymousResponse = z.infer<typeof CreateAnonymousResponseSchema>;

export const CreateChartProfileRequestSchema = z.object({
  display_name: z.string(),
  birth_info: TuviTimeSchema.extend({
    calendar: z.literal('solar'),
  }),
});
export type CreateChartProfileRequest = z.infer<typeof CreateChartProfileRequestSchema>;

export const ChartProfileSchema = z.object({
  id: z.string(),
  display_name: z.string(),
  birth_info: CreateChartProfileRequestSchema.shape.birth_info,
  created_at: z.string(),
  updated_at: z.string(),
});
export type ChartProfile = z.infer<typeof ChartProfileSchema>;

export const CreateChartProfileResponseSchema = z.object({
  chart_profile: ChartProfileSchema,
});
export type CreateChartProfileResponse = z.infer<typeof CreateChartProfileResponseSchema>;

export const ListChartProfilesResponseSchema = z.object({
  chart_profiles: z.array(ChartProfileSchema),
});
export type ListChartProfilesResponse = z.infer<typeof ListChartProfilesResponseSchema>;

export const ChatMessageSchema = z.object({
  id: z.string(),
  role: z.enum(['user', 'assistant']),
  content: z.string(),
  status: z.enum(['pending', 'confirmed', 'failed', 'cancelled']),
  created_at: z.string(),
  updated_at: z.string(),
});
export type PersistedChatMessage = z.infer<typeof ChatMessageSchema>;

export const ChatSessionSchema = z.object({
  id: z.string(),
  chart_profile_id: z.string(),
  title: z.string().nullable(),
  messages: z.array(ChatMessageSchema),
  created_at: z.string(),
  updated_at: z.string(),
});
export type ChatSession = z.infer<typeof ChatSessionSchema>;

export const ChatSessionSummarySchema = ChatSessionSchema.omit({ messages: true }).extend({
  message_count: z.number().int(),
});
export type ChatSessionSummary = z.infer<typeof ChatSessionSummarySchema>;

export const CreateSessionRequestSchema = z.object({
  title: z.string().nullable(),
});
export type CreateSessionRequest = z.infer<typeof CreateSessionRequestSchema>;

export const CreateSessionResponseSchema = z.object({
  session: ChatSessionSchema,
});
export type CreateSessionResponse = z.infer<typeof CreateSessionResponseSchema>;

export const GetSessionResponseSchema = z.object({
  session: ChatSessionSchema,
});
export type GetSessionResponse = z.infer<typeof GetSessionResponseSchema>;

export const ListSessionsResponseSchema = z.object({
  sessions: z.array(ChatSessionSummarySchema),
});
export type ListSessionsResponse = z.infer<typeof ListSessionsResponseSchema>;

export const SessionChatStreamRequestSchema = z.object({
  content: z.string().min(1),
});
export type SessionChatStreamRequest = z.infer<typeof SessionChatStreamRequestSchema>;

export const ChatToolCallSchema = z.object({
  id: z.string().nullable().optional(),
  name: z.string(),
  arguments: z.unknown(),
});
export type ChatToolCall = z.infer<typeof ChatToolCallSchema>;

export const ChatDebugEventSchema = z.object({
  type: z.enum(['tool_call', 'tool_result', 'result']),
  id: z.string().nullable().optional(),
  name: z.string().nullable().optional(),
  arguments: z.unknown().optional(),
  content: z.unknown().optional(),
  output: z.unknown().optional(),
});
export type ChatDebugEvent = z.infer<typeof ChatDebugEventSchema>;

export const ChatResponseSchema = z.object({
  answer: z.string(),
  tool_calls: z.array(ChatToolCallSchema),
  debug_events: z.array(ChatDebugEventSchema).default([]),
});
export type ChatResponse = z.infer<typeof ChatResponseSchema>;
