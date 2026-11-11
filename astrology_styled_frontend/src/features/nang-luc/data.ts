"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { z } from "zod";
import { useAccountRequestScope } from "@/lib/api/account-request";
import { request } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/queryKeys";
import type { BirthInfo } from "@/lib/api/schemas";
import { safeStorage } from "@/lib/safe-storage";

/** Coins on the normal plan; the backend charges each account once per chart. */
export const CAPABILITY_REPORT_COST = 10;

const description = { mo_ta: z.string().min(1), giai_thich: z.string().min(1) };
export const capabilitySchema = z.object({
  tong_quan: z.string().min(1),
  diem_manh: z
    .array(
      z.object({ nang_luc_id: z.string().min(1), nang_luc: z.string().min(1), ...description }),
    )
    .max(6),
  diem_yeu: z
    .array(
      z.object({
        ten: z.string().min(1),
        loai: z.enum(["han_che_truc_tiep", "qua_da", "xung_dot"]),
        ...description,
      }),
    )
    .max(6),
});
export type CapabilityProfile = z.infer<typeof capabilitySchema>;
export function capabilityKey(birth: BirthInfo | null, userId: string | null | undefined) {
  return birth && userId
    ? `v1:${userId}:${birth.calendar}:${birth.year}:${birth.month}:${birth.day}:${birth.hour}:${birth.gender}`
    : "idle";
}
interface CapabilityState {
  entries: Record<string, { unlocked: boolean; report?: CapabilityProfile }>;
  unlock: (key: string) => void;
  save: (key: string, report: CapabilityProfile) => void;
  clear: () => void;
}
export const useCapabilityStore = create<CapabilityState>()(
  persist(
    (set) => ({
      entries: {},
      unlock: (key) =>
        set((state) => ({
          entries: { ...state.entries, [key]: { ...state.entries[key], unlocked: true } },
        })),
      // A reset during a request must never resurrect the old report.
      save: (key, report) =>
        set((state) =>
          state.entries[key]?.unlocked
            ? { entries: { ...state.entries, [key]: { unlocked: true, report } } }
            : state,
        ),
      clear: () => set({ entries: {} }),
    }),
    {
      name: "tuvi.capability-v1",
      storage: createJSONStorage(() => safeStorage),
      skipHydration: true,
      partialize: (state) => ({ entries: state.entries }),
      merge: (persisted, current) => {
        const parsed = z
          .object({
            entries: z.record(
              z.string(),
              z.object({ unlocked: z.boolean(), report: capabilitySchema.optional() }),
            ),
          })
          .safeParse(persisted);
        return parsed.success ? { ...current, entries: parsed.data.entries } : current;
      },
    },
  ),
);

export function useCapabilityReport(birth: BirthInfo | null, unlocked: boolean) {
  const { userId } = useAccountRequestScope();
  const queryClient = useQueryClient();
  const key = capabilityKey(birth, userId);
  const saved = useCapabilityStore((state) => state.entries[key]?.report);
  return useQuery({
    queryKey: ["capability", key],
    enabled: key !== "idle" && unlocked,
    initialData: saved,
    staleTime: Infinity,
    gcTime: Infinity,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    refetchOnMount: false,
    queryFn: async ({ signal }) => {
      const restored = useCapabilityStore.getState().entries[key]?.report;
      if (restored) return restored;
      const report = await request("/api/v1/laso/strength-weakness", {
        method: "POST",
        body: birth,
        schema: capabilitySchema,
        withAuth: true,
        expectedUserId: userId,
        signal,
      });
      // A reset may have unlocked the same chart again while this request ran.
      signal.throwIfAborted();
      useCapabilityStore.getState().save(key, report);
      // The first report for a chart spends coins.
      void queryClient.invalidateQueries({ queryKey: queryKeys.accountAccess(userId ?? null) });
      return report;
    },
  });
}
