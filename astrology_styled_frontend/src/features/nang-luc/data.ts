"use client";

import { skipToken, useQuery, useQueryClient } from "@tanstack/react-query";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { z } from "zod";
import type { BirthInfo } from "@/lib/api/schemas";
import { safeStorage } from "@/lib/safe-storage";

import { capabilitySchema, emptyProfile, type CapabilityProfile } from "./schema";
import { streamCapabilityReport } from "./stream";
export { capabilitySchema, type CapabilityProfile } from "./schema";
export interface CapabilityDraft {
  generation: number;
  attempt: number;
  profile: CapabilityProfile;
}

export function capabilityKey(birth: BirthInfo | null) {
  return birth
    ? `v1:${birth.calendar}:${birth.year}:${birth.month}:${birth.day}:${birth.hour}:${birth.gender}`
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
  const key = capabilityKey(birth);
  const client = useQueryClient();
  const draftKey = ["capability", key, "draft"];
  const draft = useQuery<CapabilityDraft>({
    queryKey: draftKey,
    queryFn: skipToken,
    enabled: false,
    staleTime: Infinity,
  });
  const saved = useCapabilityStore((state) => state.entries[key]?.report);
  const analysis = useQuery({
    queryKey: ["capability", key],
    enabled: birth !== null && unlocked,
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
      if (!birth) throw new Error("Thiếu thông tin lá số.");
      const generation = (client.getQueryData<CapabilityDraft>(draftKey)?.generation ?? 0) + 1;
      client.setQueryData<CapabilityDraft>(draftKey, {
        generation,
        attempt: 0,
        profile: emptyProfile(),
      });
      const report = await streamCapabilityReport(birth, signal, async (event) => {
        signal.throwIfAborted();
        client.setQueryData<CapabilityDraft>(draftKey, (current) => {
          if (event.type === "started" || event.type === "reset")
            return { generation, attempt: event.attempt, profile: emptyProfile() };
          if (!current || event.type === "error" || current.attempt !== event.attempt)
            return current;
          if (event.type === "done") return { ...current, profile: event.profile };
          if (event.type === "overview")
            return { ...current, profile: { ...current.profile, tong_quan: event.text } };
          if (event.type !== "finding") return current;
          const profile = { ...current.profile };
          if (event.kind === "strength") {
            const items = [...profile.diem_manh];
            if (event.index > items.length) throw new Error("Thứ tự điểm mạnh không hợp lệ.");
            items[event.index] = event.finding;
            profile.diem_manh = items;
          } else {
            const items = [...profile.diem_yeu];
            if (event.index > items.length) throw new Error("Thứ tự điểm yếu không hợp lệ.");
            items[event.index] = event.finding;
            profile.diem_yeu = items;
          }
          return { ...current, profile };
        });
        // A proxy can deliver several findings in one packet. Give each card
        // a short entrance without delaying readers in a background tab.
        if (event.type === "finding" && !document.hidden) {
          await new Promise<void>((resolve, reject) => {
            const finish = () => {
              signal.removeEventListener("abort", abort);
              resolve();
            };
            const timer = setTimeout(finish, 160);
            const abort = () => {
              clearTimeout(timer);
              reject(signal.reason);
            };
            signal.addEventListener("abort", abort, { once: true });
          });
        }
      });
      // A reset may have unlocked the same chart again while this request ran.
      signal.throwIfAborted();
      useCapabilityStore.getState().save(key, report);
      return report;
    },
  });
  return { ...analysis, draft: draft.data };
}
