import { Effect, Schema, SchemaGetter, Struct } from "effect";

import { IntBetween, IsoDateTime, NonEmpty } from "@/lib/schema";

/**
 * Effect Schema mirrors of the backend contract.
 *
 * Sources: `api/schemas.py` and `api/chat/models.py`. When either changes,
 * change these — a drift shows up as a `parse` error carrying the issues,
 * which is the point.
 */

const nullByDefault = <S extends Schema.Constraint & { readonly Encoded: unknown }>(schema: S) =>
  Schema.NullOr(schema).pipe(Schema.withDecodingDefault(Effect.succeed(null)));

const falseByDefault = Schema.Boolean.pipe(Schema.withDecodingDefault(Effect.succeed(false)));

const Coins = IntBetween(1, Number.MAX_SAFE_INTEGER);

export const accountAccessSchema = Schema.Struct({
  user_id: Schema.String,
  role: Schema.Literals(["user", "admin"]),
  plan: Schema.Literals(["normal", "full_unlock"]),
  balance: IntBetween(0, Number.MAX_SAFE_INTEGER),
});

export type AccountAccess = typeof accountAccessSchema.Type;

/** The code is trimmed and upper-cased before it is sent. */
export const redeemCodeRequestSchema = Schema.Struct({
  code: Schema.Trim.pipe(
    Schema.decodeTo(NonEmpty, {
      decode: SchemaGetter.toUpperCase(),
      encode: SchemaGetter.passthrough(),
    }),
  ),
});

export const redeemCodeResponseSchema = Schema.Struct({
  coins: Coins,
});

export const createRedeemCodeRequestSchema = Schema.Struct({
  coins: Coins,
  kind: Schema.Literals(["single_use", "per_account"]),
  expires_at: IsoDateTime,
});

export type CreateRedeemCodeRequest = typeof createRedeemCodeRequestSchema.Type;

export const createRedeemCodeResponseSchema = createRedeemCodeRequestSchema.mapFields(
  Struct.assign({ code: NonEmpty }),
);

// --- api/chat/models.py ----------------------------------------------------

export const birthInfoSchema = Schema.Struct({
  calendar: Schema.Literal("solar").pipe(
    Schema.withDecodingDefault(Effect.succeed("solar" as const)),
  ),
  year: IntBetween(1900, 2099),
  month: IntBetween(1, 12),
  day: IntBetween(1, 31),
  hour: IntBetween(0, 23),
  gender: Schema.Literals(["M", "F"]),
});

export type BirthInfo = typeof birthInfoSchema.Type;

export const chatRoleSchema = Schema.Literals(["user", "assistant"]);

export const chatMessageStatusSchema = Schema.Literals([
  "pending",
  "confirmed",
  "failed",
  "cancelled",
]);

export const chatMessageSchema = Schema.Struct({
  id: Schema.String,
  role: chatRoleSchema,
  content: Schema.String,
  status: chatMessageStatusSchema,
  created_at: IsoDateTime,
  updated_at: IsoDateTime,
});

export type ChatMessage = typeof chatMessageSchema.Type;

export const chatSessionSchema = Schema.Struct({
  id: Schema.String,
  chart_profile_id: Schema.String,
  title: nullByDefault(Schema.String),
  messages: Schema.Array(chatMessageSchema),
  created_at: IsoDateTime,
  updated_at: IsoDateTime,
});

export type ChatSession = typeof chatSessionSchema.Type;

export const chatSessionSummarySchema = Schema.Struct({
  id: Schema.String,
  chart_profile_id: Schema.String,
  title: nullByDefault(Schema.String),
  message_count: Schema.Number.check(Schema.isInt()),
  created_at: IsoDateTime,
  updated_at: IsoDateTime,
});

export type ChatSessionSummary = typeof chatSessionSummarySchema.Type;

// --- chat stream events (SSE) ----------------------------------------------

/**
 * Terminal statuses the `done` event can carry. Wider than
 * `chatMessageStatusSchema` because a duplicate in-progress stream also ends
 * with `done` carrying `duplicate_in_progress` — see `api/chat/routes.py`.
 */
export const sseDoneStatusSchema = Schema.Literals([
  "confirmed",
  "failed",
  "cancelled",
  "duplicate_in_progress",
]);

export const sseIdsEventSchema = Schema.Struct({
  type: Schema.Literal("ids"),
  user_message_id: Schema.String,
  assistant_message_id: Schema.String,
});

export const sseTextEventSchema = Schema.Struct({
  type: Schema.Literal("text"),
  delta: Schema.String,
});

export const sseToolCallEventSchema = Schema.Struct({
  type: Schema.Literal("tool_call"),
  id: Schema.String,
  name: Schema.String,
  arguments: Schema.optionalKey(Schema.Unknown),
});

export const sseToolResultEventSchema = Schema.Struct({
  type: Schema.Literal("tool_result"),
  id: Schema.optional(Schema.NullOr(Schema.String)),
  name: Schema.optional(Schema.NullOr(Schema.String)),
  content: Schema.optionalKey(Schema.Unknown),
});

export const sseResultEventSchema = Schema.Struct({
  type: Schema.Literal("result"),
  output: Schema.optionalKey(Schema.Unknown),
});

export const sseErrorEventSchema = Schema.Struct({
  type: Schema.Literal("error"),
  message: Schema.String,
});

export const sseDoneEventSchema = Schema.Struct({
  type: Schema.Literal("done"),
  status: sseDoneStatusSchema,
});

export const sseDuplicateInProgressEventSchema = Schema.Struct({
  type: Schema.Literal("duplicate_in_progress"),
  user_message_id: Schema.String,
  assistant_message_id: Schema.String,
  status: chatMessageStatusSchema,
});

export const sseChatEventSchema = Schema.Union([
  sseIdsEventSchema,
  sseTextEventSchema,
  sseToolCallEventSchema,
  sseToolResultEventSchema,
  sseResultEventSchema,
  sseErrorEventSchema,
  sseDoneEventSchema,
  sseDuplicateInProgressEventSchema,
]);

export type SseChatEvent = typeof sseChatEventSchema.Type;

// --- api/schemas.py --------------------------------------------------------

export const starSchema = Schema.Struct({
  name: Schema.String,
  display: Schema.String,
  element: Schema.String,
});

export const cungSchema = Schema.Struct({
  position: Schema.String,
  role: nullByDefault(Schema.String),
  chinh_tinh: Schema.Array(Schema.String),
  phu_tinh: Schema.Array(starSchema),
  tuhoa: Schema.Array(Schema.String),
  trang_sinh: nullByDefault(Schema.String),
  is_tuan: falseByDefault,
  is_triet: falseByDefault,
  is_cung_than: falseByDefault,
  age_daivan: nullByDefault(Schema.Number.check(Schema.isInt())),
  saoLuu: Schema.Array(starSchema),
});

export type Cung = typeof cungSchema.Type;

/**
 * Foundation fields — stable keys the deck keys content off. Required, never
 * optional: a chart missing them cannot render the deck, and a half-rendered
 * screen is worse than a recast. Mirrors the `Literal` unions in
 * `api/schemas.py`.
 */
export const menhCucRelationSchema = Schema.Literals([
  "sinh_xuat",
  "sinh_nhap",
  "khac_xuat",
  "khac_nhap",
  "binh_hoa",
]);

export const amDuongRelationSchema = Schema.Literals(["thuan_ly", "nghich_ly"]);

export const diaChiSchema = Schema.Literals([
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

export const nguHanhSchema = Schema.Literals(["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]);

export type MenhCucRelation = typeof menhCucRelationSchema.Type;
export type AmDuongRelation = typeof amDuongRelationSchema.Type;
export type DiaChi = typeof diaChiSchema.Type;
export type NguHanh = typeof nguHanhSchema.Type;

export const buildLasoResponseSchema = Schema.Struct({
  id: Schema.String,
  summary: Schema.String,
  ban_menh_name: Schema.String,
  cuc_name: Schema.String,
  menh_cuc_relation_label: Schema.String,
  menh_cuc_relation: menhCucRelationSchema,
  am_duong_relation: amDuongRelationSchema,
  dia_chi_natal_year: diaChiSchema,
  ban_menh_ngu_hanh: nguHanhSchema,
  cung_by_position: Schema.Record(Schema.String, cungSchema),
});

export type BuildLasoResponse = typeof buildLasoResponseSchema.Type;

export const buildSaoLuuRequestSchema = Schema.Struct({
  observation_time: birthInfoSchema,
});

export const buildSaoLuuResponseSchema = Schema.Struct({
  cung_by_position: Schema.Record(Schema.String, cungSchema),
});

/**
 * `POST /laso/preview`. Gender is omitted: cung Mệnh's chính tinh do not
 * depend on it, and the preview is meant to fire before the user picks one.
 */
export const previewLasoRequestSchema = birthInfoSchema.mapFields(Struct.omit(["gender"]));

export type PreviewLasoRequest = typeof previewLasoRequestSchema.Type;

export const previewLasoResponseSchema = Schema.Struct({
  /** Clean star names — no trạng thái suffix. Empty for vô chính diệu. */
  chinh_tinh: Schema.Array(Schema.String),
  menh_position: Schema.String,
});

export type PreviewLasoResponse = typeof previewLasoResponseSchema.Type;

export const chartProfileSchema = Schema.Struct({
  id: Schema.String,
  display_name: Schema.String,
  birth_info: birthInfoSchema,
  created_at: IsoDateTime,
  updated_at: IsoDateTime,
});

export type ChartProfile = typeof chartProfileSchema.Type;

export const createChartProfileRequestSchema = Schema.Struct({
  display_name: Schema.String,
  birth_info: birthInfoSchema,
});

export type CreateChartProfileRequest = typeof createChartProfileRequestSchema.Type;

export const renameChartProfileRequestSchema = Schema.Struct({
  display_name: Schema.Trim.check(Schema.isMinLength(1), Schema.isMaxLength(80)),
});

export const createChartProfileResponseSchema = Schema.Struct({
  chart_profile: chartProfileSchema,
});

/**
 * `DELETE /api/v1/chart-profiles/{id}` answers `204` with no body, which the
 * client's `safeBody` turns into `null`. Delete requests decode their response
 * with this rather than a JSON schema. Any future 204 endpoint reuses it.
 */
export const emptyResponseSchema = Schema.Null;

export const listChartProfilesResponseSchema = Schema.Struct({
  chart_profiles: Schema.Array(chartProfileSchema),
});

export const createSessionRequestSchema = Schema.Struct({
  title: Schema.optional(Schema.NullOr(Schema.String)),
});

export const createSessionResponseSchema = Schema.Struct({
  session: chatSessionSchema,
});

export const getSessionResponseSchema = Schema.Struct({
  session: chatSessionSchema,
});

export const listSessionsResponseSchema = Schema.Struct({
  sessions: Schema.Array(chatSessionSummarySchema),
});

export const healthResponseSchema = Schema.Struct({
  status: Schema.String,
});
