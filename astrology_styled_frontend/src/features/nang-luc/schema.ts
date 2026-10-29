import { z } from "zod";

const description = { mo_ta: z.string().min(1), giai_thich: z.string().min(1) };
export const strengthSchema = z.object({
  nang_luc_id: z.string().min(1),
  nang_luc: z.string().min(1),
  ...description,
});
export const weaknessSchema = z.object({
  ten: z.string().min(1),
  loai: z.enum(["han_che_truc_tiep", "qua_da", "xung_dot"]),
  ...description,
});
export const capabilitySchema = z.object({
  tong_quan: z.string().min(1),
  diem_manh: z.array(strengthSchema).max(6),
  diem_yeu: z.array(weaknessSchema).max(6),
});
export type CapabilityProfile = z.infer<typeof capabilitySchema>;
export const emptyProfile = (): CapabilityProfile => ({
  tong_quan: "",
  diem_manh: [],
  diem_yeu: [],
});

const attempt = { attempt: z.number().int().nonnegative() };
const finding = {
  type: z.literal("finding"),
  ...attempt,
  id: z.string(),
  index: z.number().int().min(0).max(5),
};
export const capabilityEventSchema = z.union([
  z.object({ type: z.enum(["started", "reset"]), ...attempt }),
  z.object({ type: z.literal("overview"), ...attempt, text: z.string().min(1) }),
  z.object({ ...finding, kind: z.literal("strength"), finding: strengthSchema }),
  z.object({ ...finding, kind: z.literal("weakness"), finding: weaknessSchema }),
  z.object({ type: z.literal("done"), ...attempt, profile: capabilitySchema }),
  z.object({ type: z.literal("error"), message: z.string().min(1) }),
]);
export type CapabilityEvent = z.infer<typeof capabilityEventSchema>;
