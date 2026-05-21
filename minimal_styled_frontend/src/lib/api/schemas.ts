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
});
export type Star = z.infer<typeof StarSchema>;

export const CungSchema = z.object({
  position: z.string(),
  role: z.string().nullable().optional(),
  chinh_tinh: z.array(z.string()),
  phu_tinh: z.array(StarSchema),
  tuhoa: z.array(z.string()),
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
