"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { BuildLasoRequest, SessionStash, UserProfile } from "../_lib/types";
import { buildLaso } from "@/services/api/v1/laso/build";
import {
  createChatSession,
  deleteChartProfile,
  deleteChatSession,
  listChartProfiles,
  listChatSessions,
  type ChartProfilePayload,
  type ChatSessionSummaryPayload,
} from "@/services/api/v1/conversation-history";
import { Eyebrow } from "./Eyebrow";
import { Btn } from "./Buttons";

interface LichSuDrawerProps {
  stash: SessionStash;
  onSessionChange: (stash: SessionStash) => void;
  onCurrentDeleted: () => void;
  onClose: () => void;
}

export function LichSuDrawer({
  stash,
  onSessionChange,
  onCurrentDeleted,
  onClose,
}: LichSuDrawerProps) {
  const router = useRouter();
  const ownerId = stash.ownerId;
  const [profiles, setProfiles] = useState<ChartProfilePayload[] | null>(null);
  const [sessionsByProfile, setSessionsByProfile] = useState<Record<string, ChatSessionSummaryPayload[]>>({});
  const [selectedProfileId, setSelectedProfileId] = useState<string | null>(stash.chartProfileId ?? null);
  const [profileReload, setProfileReload] = useState(0);
  const [sessionReload, setSessionReload] = useState(0);
  const [mutating, setMutating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ownerId) return;

    let cancelled = false;
    void listChartProfiles({ ownerId })
      .then((items) => {
        if (cancelled) return;
        const sorted = sortProfiles(items);
        setProfiles(sorted);
        setError(null);
        setSelectedProfileId((current) => {
          if (current && sorted.some((p) => p.id === current)) return current;
          if (stash.chartProfileId && sorted.some((p) => p.id === stash.chartProfileId)) {
            return stash.chartProfileId;
          }
          return sorted[0]?.id ?? null;
        });
      })
      .catch((err) => {
        if (!cancelled) setError(errorMessage(err, "Không tải được hồ sơ lá số"));
      });

    return () => {
      cancelled = true;
    };
  }, [ownerId, stash.chartProfileId, profileReload]);

  useEffect(() => {
    if (!ownerId || !selectedProfileId) return;

    let cancelled = false;
    void listChatSessions({ ownerId, chartProfileId: selectedProfileId })
      .then((items) => {
        if (cancelled) return;
        setError(null);
        setSessionsByProfile((current) => ({
          ...current,
          [selectedProfileId]: sortSessions(items),
        }));
      })
      .catch((err) => {
        if (!cancelled) setError(errorMessage(err, "Không tải được phiên trò chuyện"));
      });
    return () => {
      cancelled = true;
    };
  }, [ownerId, selectedProfileId, sessionReload]);

  async function openSession(profile: ChartProfilePayload, sessionId: string | null) {
    if (!ownerId || mutating) return;

    setMutating(true);
    setError(null);
    try {
      const openedSessionId =
        sessionId ??
        (await createChatSession({
          ownerId,
          chartProfileId: profile.id,
          idempotencyKey: clientOperationId(),
          title: displayName(profile),
        }));
      const laso = await buildLaso(toBuildLasoRequest(profile.birth_info));
      onSessionChange({
        laso,
        profile: toUserProfile(profile, stash),
        ownerId,
        chartProfileId: profile.id,
        sessionId: openedSessionId,
        fetchedAt: new Date().toISOString(),
      });
      onClose();
    } catch (err) {
      setError(errorMessage(err, "Không mở được phiên trò chuyện"));
    } finally {
      setMutating(false);
    }
  }

  async function removeProfile(profile: ChartProfilePayload) {
    if (!ownerId || mutating) return;
    if (!window.confirm(`Xóa toàn bộ hồ sơ "${displayName(profile)}" và các phiên trò chuyện?`)) return;

    setMutating(true);
    setError(null);
    try {
      await deleteChartProfile({ ownerId, chartProfileId: profile.id });
      const remainingProfiles = (profiles ?? []).filter((item) => item.id !== profile.id);
      setProfiles(remainingProfiles);
      setSessionsByProfile((items) => {
        const next = { ...items };
        delete next[profile.id];
        return next;
      });
      if (stash.chartProfileId === profile.id) {
        onCurrentDeleted();
        return;
      }
      if (selectedProfileId === profile.id) {
        setSelectedProfileId(remainingProfiles[0]?.id ?? null);
      }
      setProfileReload((value) => value + 1);
    } catch (err) {
      setError(errorMessage(err, "Không xoá được hồ sơ lá số"));
    } finally {
      setMutating(false);
    }
  }

  async function removeSession(profileId: string, sessionId: string) {
    if (!ownerId || mutating) return;
    if (!window.confirm("Xóa phiên trò chuyện này?")) return;

    setMutating(true);
    setError(null);
    try {
      await deleteChatSession({ ownerId, sessionId });
      setSessionsByProfile((items) => ({
        ...items,
        [profileId]: (items[profileId] ?? []).filter((item) => item.id !== sessionId),
      }));
      if (stash.sessionId === sessionId) {
        onCurrentDeleted();
        return;
      }
      setSessionReload((value) => value + 1);
    } catch (err) {
      setError(errorMessage(err, "Không xoá được phiên trò chuyện"));
    } finally {
      setMutating(false);
    }
  }

  const selectedProfile = (profiles ?? []).find((profile) => profile.id === selectedProfileId) ?? null;
  const selectedSessions = selectedProfile ? sessionsByProfile[selectedProfile.id] : undefined;
  const loadingSessions = Boolean(ownerId && selectedProfile && selectedSessions == null);
  const sessionItems = selectedSessions ?? [];

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-[rgba(244,237,224,0.55)] anim-fade-in" onClick={onClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="lichsu-title"
        className="absolute top-0 left-0 bottom-0 w-[560px] max-w-[90vw] bg-[rgba(255,252,245,0.99)] border-r-[1.5px] border-[var(--color-ink)] flex flex-col anim-slide-left"
        style={{ boxShadow: "24px 0 64px rgba(26,22,17,0.18)" }}
      >
        <div className="px-8 pt-6 pb-4 border-b border-[rgba(26,22,17,0.14)]">
          <div className="flex justify-between items-start gap-4">
            <div>
              <Eyebrow>Hồ sơ đã lưu</Eyebrow>
              <h2 id="lichsu-title" className="font-serif text-[32px] font-medium mt-1 tracking-[-0.3px]">
                Sổ tay trò chuyện
              </h2>
              <div className="text-[12px] text-[var(--color-ink-3)] mt-1">
                {sessionItems.length} phiên · {profiles?.length ?? 0} lá số
              </div>
            </div>
            <Btn variant="ghost" className="text-[16px]" onClick={onClose} aria-label="Đóng">✕</Btn>
          </div>

          <div className="flex items-center gap-3 mt-4 min-w-0">
            <label htmlFor="lichsu-profile" className="text-[11px] text-[var(--color-ink-3)] uppercase tracking-[1px]">
              Lá số
            </label>
            <select
              id="lichsu-profile"
              value={selectedProfileId ?? ""}
              disabled={!profiles?.length || mutating}
              onChange={(event) => setSelectedProfileId(event.target.value || null)}
              className="min-w-0 max-w-[220px] flex-1 bg-[var(--color-paper)] border border-[rgba(26,22,17,0.22)] px-3 py-2 text-[13px] text-[var(--color-ink)]"
            >
              {(profiles ?? []).map((profile) => (
                <option key={profile.id} value={profile.id}>
                  {displayName(profile)}
                </option>
              ))}
            </select>
            <Btn
              type="button"
              variant="ghost"
              className="text-[12px]"
              onClick={() => {
                onClose();
                router.push("/");
              }}
            >
              ＋ thêm lá số
            </Btn>
            {selectedProfile && (
              <Btn
                type="button"
                variant="ghost"
                className="ml-auto px-2 text-[14px]"
                aria-label={`Xóa hồ sơ ${displayName(selectedProfile)}`}
                disabled={mutating}
                onClick={() => void removeProfile(selectedProfile)}
              >
                ×
              </Btn>
            )}
          </div>
          {selectedProfile && (
            <div className="mt-2 text-[11px] text-[var(--color-ink-3)]">
              {formatBirth(selectedProfile)} · cập nhật {formatDateTime(selectedProfile.updated_at)}
            </div>
          )}
        </div>

        <div className="flex-1 py-2 overflow-auto">
          {!ownerId && (
            <div className="px-8 py-4 font-serif italic text-[14px] text-[var(--color-ink-3)]">
              An lại lá số để tạo hồ sơ backend.
            </div>
          )}
          {error && (
            <div className="px-8 py-4 font-serif italic text-[14px] text-[var(--color-crimson)]" role="alert">
              {error}
            </div>
          )}
          {ownerId && profiles === null && (
            <div className="px-8 py-4 font-serif italic text-[14px] text-[var(--color-ink-3)]">
              Đang tải hồ sơ...
            </div>
          )}
          {ownerId && profiles?.length === 0 && (
            <div className="px-8 py-4 font-serif italic text-[14px] text-[var(--color-ink-3)]">
              Chưa có hồ sơ lá số nào.
            </div>
          )}
          {loadingSessions && (
            <div className="px-8 py-4 font-serif italic text-[14px] text-[var(--color-ink-3)]">
              Đang tải phiên...
            </div>
          )}
          {!loadingSessions && selectedProfile && sessionItems.length === 0 && (
            <div className="px-8 py-4 font-serif italic text-[14px] text-[var(--color-ink-3)]">
              Chưa có phiên cho lá số này.
            </div>
          )}
          {selectedProfile && sessionItems.map((session) => {
            const active = session.id === stash.sessionId;
            return (
              <div key={session.id} className="flex items-stretch gap-1 border-b border-[rgba(26,22,17,0.08)] px-6 py-1">
                <button
                  type="button"
                  disabled={mutating}
                  onClick={() => void openSession(selectedProfile, session.id)}
                  className="min-w-0 flex-1 text-left px-3 py-3 cursor-pointer disabled:opacity-50"
                  style={{
                    borderLeft: active ? "3px solid var(--color-crimson)" : "3px solid transparent",
                    background: active ? "rgba(139,42,31,0.06)" : "transparent",
                  }}
                >
                  <div className="flex justify-between gap-3">
                    <span className="min-w-0 flex-1 truncate font-serif text-[16px]">
                      {session.title?.trim() || "Phiên trò chuyện"}
                    </span>
                    <span className="shrink-0 text-[11px] text-[var(--color-ink-3)]">
                      {formatTime(session.updated_at)}
                    </span>
                  </div>
                  <div className="mt-1 text-[11px] text-[var(--color-ink-3)]">
                    {formatDateTime(session.updated_at)} · {session.message_count} tin
                  </div>
                </button>
                <Btn
                  type="button"
                  variant="ghost"
                  className="px-2 text-[14px]"
                  aria-label="Xóa phiên trò chuyện"
                  disabled={mutating}
                  onClick={() => void removeSession(selectedProfile.id, session.id)}
                >
                  ×
                </Btn>
              </div>
            );
          })}
        </div>

        <div className="px-8 py-4 border-t border-[rgba(26,22,17,0.14)]">
          <Btn
            type="button"
            variant="crimson"
            className="w-full justify-center"
            disabled={!selectedProfile || mutating}
            onClick={() => selectedProfile && void openSession(selectedProfile, null)}
          >
            ＋ Bắt đầu phiên mới
          </Btn>
        </div>
      </div>
    </div>
  );
}

function sortProfiles(profiles: ChartProfilePayload[]): ChartProfilePayload[] {
  return [...profiles].sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at));
}

function sortSessions(sessions: ChatSessionSummaryPayload[]): ChatSessionSummaryPayload[] {
  return [...sessions].sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at));
}

function toBuildLasoRequest(birthInfo: ChartProfilePayload["birth_info"]): BuildLasoRequest {
  const { day, month, year, gender } = birthInfo;
  if (birthInfo.calendar === "lunar") {
    return {
      calendar: "lunar",
      day,
      month,
      year,
      hour_in_dia_chi: birthInfo.hour_in_dia_chi,
      is_leap_month: birthInfo.is_leap_month ?? false,
      gender,
    };
  }
  return { calendar: "solar", day, month, year, hour: birthInfo.hour ?? 0, gender };
}

function toUserProfile(profile: ChartProfilePayload, current: SessionStash): UserProfile {
  const cached = current.chartProfileId === profile.id ? current.profile : null;
  const calendar = profile.birth_info.calendar === "lunar" ? "am" : cached?.calendar ?? "duong";
  return {
    name: displayName(profile),
    gender: profile.birth_info.gender,
    calendar,
    day: profile.birth_info.day,
    month: profile.birth_info.month,
    year: profile.birth_info.year,
    hour: profile.birth_info.hour ?? cached?.hour ?? 0,
    minute: cached?.minute ?? 0,
    hour_in_dia_chi: profile.birth_info.hour_in_dia_chi ?? cached?.hour_in_dia_chi,
    is_leap_month: profile.birth_info.is_leap_month ?? cached?.is_leap_month,
  };
}

function displayName(profile: ChartProfilePayload): string {
  return profile.display_name.trim() || "Không tên";
}

function formatBirth(profile: ChartProfilePayload): string {
  const { day, month, year } = profile.birth_info;
  const calendar = profile.birth_info.calendar === "lunar" ? "Âm" : "Dương";
  const leap = profile.birth_info.is_leap_month ? " nhuận" : "";
  return `${String(day).padStart(2, "0")}/${String(month).padStart(2, "0")}${leap}/${year} ${calendar}`;
}

function formatDateTime(raw: string): string {
  const value = new Date(raw);
  return new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(value);
}

function formatTime(raw: string): string {
  const value = new Date(raw);
  return new Intl.DateTimeFormat("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(value);
}

function clientOperationId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof Error ? err.message : fallback;
}
