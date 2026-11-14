"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { Option, Schema } from "effect";
import { useAccountRequestScope } from "@/lib/api/account-request";
import { request } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/queryKeys";
import type { BirthInfo } from "@/lib/api/schemas";
import { safeStorage } from "@/lib/safe-storage";
import { NonEmpty } from "@/lib/schema";

/** Coins on the normal plan; the backend charges each account once per chart. */
export const CAPABILITY_REPORT_COST = 10;

const description = { mo_ta: NonEmpty, giai_thich: NonEmpty };
export const capabilitySchema = Schema.Struct({
  tong_quan: NonEmpty,
  diem_manh: Schema.Array(
    Schema.Struct({ nang_luc_id: NonEmpty, nang_luc: NonEmpty, ...description }),
  ).check(Schema.isMaxLength(6)),
  diem_yeu: Schema.Array(
    Schema.Struct({
      ten: NonEmpty,
      loai: Schema.Literals(["han_che_truc_tiep", "qua_da", "xung_dot"]),
      ...description,
    }),
  ).check(Schema.isMaxLength(6)),
});
export type CapabilityProfile = typeof capabilitySchema.Type;
const persistedEntriesSchema = Schema.Struct({
  entries: Schema.Record(
    Schema.String,
    Schema.Struct({ unlocked: Schema.Boolean, report: Schema.optionalKey(capabilitySchema) }),
  ),
});
const decodePersistedEntries = Schema.decodeUnknownOption(persistedEntriesSchema);
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
        const parsed = decodePersistedEntries(persisted);
        return Option.match(parsed, {
          onNone: () => current,
          onSome: ({ entries }) => ({ ...current, entries: { ...entries } }),
        });
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
