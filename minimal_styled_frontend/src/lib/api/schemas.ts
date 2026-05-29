import { z } from 'zod';

export const GenderSchema = z.enum(['M', 'F']);
export type Gender = z.infer<typeof GenderSchema>;

export const TuviTimeSchema = z.object({
  date: z.number().int().min(1).max(31),
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

export const ChatRequestSchema = z.object({
  message: z.string(),
});
export type ChatRequest = z.infer<typeof ChatRequestSchema>;

export const ChatToolCallSchema = z.object({
  id: z.string().nullable().optional(),
  name: z.string(),
  arguments: z.unknown(),
});
export type ChatToolCall = z.infer<typeof ChatToolCallSchema>;

export const ChatResponseSchema = z.object({
  answer: z.string(),
  tool_calls: z.array(ChatToolCallSchema),
});
export type ChatResponse = z.infer<typeof ChatResponseSchema>;

/**
 * Sentinel `answer` returned by `POST /api/v1/chat` when the backend
 * has no `la_so` in process state (see `api/main.py::chat_dummy`).
 * Match the backend string exactly; a schema-test asserts they agree.
 */
export const NO_LASO_SENTINEL = 'TinhBan chưa được tạo trong state.';
