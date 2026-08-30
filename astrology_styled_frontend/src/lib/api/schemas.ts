import { z } from "zod";

/**
 * Zod mirrors of the backend contract.
 *
 * Sources: `api/schemas.py` and `api/chat/models.py`. When either changes,
 * change these — a drift shows up as a `parse` error carrying the issues,
 * which is the point.
 */

// --- api/chat/models.py ----------------------------------------------------

export const birthInfoSchema = z.object({
  calendar: z.literal("solar").default("solar"),
  year: z.number().int().min(1900).max(2099),
  month: z.number().int().min(1).max(12),
  day: z.number().int().min(1).max(31),
  hour: z.number().int().min(0).max(23),
  gender: z.enum(["M", "F"]),
});

export type BirthInfo = z.infer<typeof birthInfoSchema>;

export const chatRoleSchema = z.enum(["user", "assistant"]);

export const chatMessageStatusSchema = z.enum(["pending", "confirmed", "failed", "cancelled"]);

export const chatMessageSchema = z.object({
  id: z.string(),
  role: chatRoleSchema,
  content: z.string(),
  status: chatMessageStatusSchema,
  created_at: z.iso.datetime({ offset: true }),
  updated_at: z.iso.datetime({ offset: true }),
});

export type ChatMessage = z.infer<typeof chatMessageSchema>;

export const chatSessionSchema = z.object({
  id: z.string(),
  chart_profile_id: z.string(),
  title: z.string().nullable().default(null),
  messages: z.array(chatMessageSchema),
  created_at: z.iso.datetime({ offset: true }),
  updated_at: z.iso.datetime({ offset: true }),
});

export type ChatSession = z.infer<typeof chatSessionSchema>;

export const chatSessionSummarySchema = z.object({
  id: z.string(),
  chart_profile_id: z.string(),
  title: z.string().nullable().default(null),
  message_count: z.number().int(),
  created_at: z.iso.datetime({ offset: true }),
  updated_at: z.iso.datetime({ offset: true }),
});

export type ChatSessionSummary = z.infer<typeof chatSessionSummarySchema>;

// --- chat stream events (SSE) ----------------------------------------------

/**
 * Terminal statuses the `done` event can carry. Wider than
 * `chatMessageStatusSchema` because a duplicate in-progress stream also ends
 * with `done` carrying `duplicate_in_progress` — see `api/chat/routes.py`.
 */
export const sseDoneStatusSchema = z.enum([
  "confirmed",
  "failed",
  "cancelled",
  "duplicate_in_progress",
]);

export const sseIdsEventSchema = z.object({
  type: z.literal("ids"),
  user_message_id: z.string(),
  assistant_message_id: z.string(),
});

export const sseTextEventSchema = z.object({
  type: z.literal("text"),
  delta: z.string(),
});

export const sseToolCallEventSchema = z.object({
  type: z.literal("tool_call"),
  id: z.string(),
  name: z.string(),
  arguments: z.unknown(),
});

export const sseToolResultEventSchema = z.object({
  type: z.literal("tool_result"),
  id: z.string().nullable().optional(),
  name: z.string().nullable().optional(),
  content: z.unknown(),
});

export const sseResultEventSchema = z.object({
  type: z.literal("result"),
  output: z.unknown(),
});

export const sseErrorEventSchema = z.object({
  type: z.literal("error"),
  message: z.string(),
});

export const sseDoneEventSchema = z.object({
  type: z.literal("done"),
  status: sseDoneStatusSchema,
});

export const sseDuplicateInProgressEventSchema = z.object({
  type: z.literal("duplicate_in_progress"),
  user_message_id: z.string(),
  assistant_message_id: z.string(),
  status: chatMessageStatusSchema,
});

export const sseChatEventSchema = z.discriminatedUnion("type", [
  sseIdsEventSchema,
  sseTextEventSchema,
  sseToolCallEventSchema,
  sseToolResultEventSchema,
  sseResultEventSchema,
  sseErrorEventSchema,
  sseDoneEventSchema,
  sseDuplicateInProgressEventSchema,
]);

export type SseChatEvent = z.infer<typeof sseChatEventSchema>;

// --- api/schemas.py --------------------------------------------------------

export const starSchema = z.object({
  name: z.string(),
  display: z.string(),
  element: z.string(),
});

export const cungSchema = z.object({
  position: z.string(),
  role: z.string().nullable().default(null),
  chinh_tinh: z.array(z.string()),
  phu_tinh: z.array(starSchema),
  tuhoa: z.array(z.string()),
  trang_sinh: z.string().nullable().default(null),
  is_tuan: z.boolean().default(false),
  is_triet: z.boolean().default(false),
  is_cung_than: z.boolean().default(false),
  age_daivan: z.number().int().nullable().default(null),
  saoLuu: z.array(starSchema),
});

export type Cung = z.infer<typeof cungSchema>;

/**
 * Foundation fields — stable keys the deck keys content off. Required, never
 * optional: a chart missing them cannot render the deck, and a half-rendered
 * screen is worse than a recast. Mirrors the `Literal` unions in
 * `api/schemas.py`.
 */
export const menhCucRelationSchema = z.enum([
  "sinh_xuat",
  "sinh_nhap",
  "khac_xuat",
  "khac_nhap",
  "binh_hoa",
]);

export const amDuongRelationSchema = z.enum(["thuan_ly", "nghich_ly"]);

export const diaChiSchema = z.enum([
  "ty",
  "suu",
  "dan",
  "meo",
  "thin",
  "ti",
  "ngo",
  "mui",
  "than",
  "dau",
  "tuat",
  "hoi",
]);

export const nguHanhSchema = z.enum(["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]);

export type MenhCucRelation = z.infer<typeof menhCucRelationSchema>;
export type AmDuongRelation = z.infer<typeof amDuongRelationSchema>;
export type DiaChi = z.infer<typeof diaChiSchema>;
export type NguHanh = z.infer<typeof nguHanhSchema>;

export const buildLasoResponseSchema = z.object({
  id: z.string(),
  summary: z.string(),
  ban_menh_name: z.string(),
  cuc_name: z.string(),
  menh_cuc_relation_label: z.string(),
  menh_cuc_relation: menhCucRelationSchema,
  am_duong_relation: amDuongRelationSchema,
  dia_chi_natal_year: diaChiSchema,
  ban_menh_ngu_hanh: nguHanhSchema,
  cung_by_position: z.record(z.string(), cungSchema),
});

export type BuildLasoResponse = z.infer<typeof buildLasoResponseSchema>;

export const buildSaoLuuRequestSchema = z.object({
  observation_time: birthInfoSchema,
});

export const buildSaoLuuResponseSchema = z.object({
  cung_by_position: z.record(z.string(), cungSchema),
});

/**
 * `POST /laso/preview`. Gender is omitted: cung Mệnh's chính tinh do not
 * depend on it, and the preview is meant to fire before the user picks one.
 */
export const previewLasoRequestSchema = birthInfoSchema.omit({ gender: true });

export type PreviewLasoRequest = z.infer<typeof previewLasoRequestSchema>;

export const previewLasoResponseSchema = z.object({
  /** Clean star names — no trạng thái suffix. Empty for vô chính diệu. */
  chinh_tinh: z.array(z.string()),
  menh_position: z.string(),
});

export type PreviewLasoResponse = z.infer<typeof previewLasoResponseSchema>;

export const createAnonymousResponseSchema = z.object({
  owner_id: z.string(),
});

export const chartProfileSchema = z.object({
  id: z.string(),
  display_name: z.string(),
  birth_info: birthInfoSchema,
  created_at: z.iso.datetime({ offset: true }),
  updated_at: z.iso.datetime({ offset: true }),
});

export type ChartProfile = z.infer<typeof chartProfileSchema>;

export const createChartProfileRequestSchema = z.object({
  display_name: z.string(),
  birth_info: birthInfoSchema,
});

export type CreateChartProfileRequest = z.infer<typeof createChartProfileRequestSchema>;

export const createChartProfileResponseSchema = z.object({
  chart_profile: chartProfileSchema,
});

/**
 * `DELETE /api/v1/chart-profiles/{id}` answers `204` with no body, which the
 * client's `safeBody` turns into `null`. Delete hooks parse their response
 * with this rather than a JSON schema. Any future 204 endpoint reuses it.
 */
export const emptyResponseSchema = z.null();

export const listChartProfilesResponseSchema = z.object({
  chart_profiles: z.array(chartProfileSchema),
});

export const createSessionRequestSchema = z.object({
  title: z.string().nullable().optional(),
});

export const createSessionResponseSchema = z.object({
  session: chatSessionSchema,
});

export const getSessionResponseSchema = z.object({
  session: chatSessionSchema,
});

export const listSessionsResponseSchema = z.object({
  sessions: z.array(chatSessionSummarySchema),
});

export const healthResponseSchema = z.object({
  status: z.string(),
  la_so_created: z.boolean(),
});
