"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import type {
  ChatMessage as Msg,
  ChatToolEntry,
  ChatMessageRole,
  CungPayload,
  OverlayKind,
  SessionStash,
} from "../_lib/types";
import {
  DEFAULT_VIEW_YEAR,
  buildRequestFromProfile,
  diaChiForYear,
  formatViewYearLabel,
  withSaoLuuOverlay,
  VIEW_YEAR_MAX,
  VIEW_YEAR_MIN,
} from "../_lib/sao-luu-overlay";
import { clearStash, loadStash, saveStash } from "../_lib/session-store";
import { useStreamChat } from "@/services/api/v1/chat/send";
import { getChatSession, type ChatMessagePayload } from "@/services/api/v1/conversation-history";
import { buildSaoLuu } from "@/services/api/v1/laso/build";
import { TopBar } from "./TopBar";
import { TopBarMenu } from "./TopBarMenu";
import { LeftRail } from "./LeftRail";
import { ChatPanel } from "./ChatPanel";
import { RightRail } from "./RightRail";
import { DaiVanModal } from "./DaiVanModal";
import { LichSuDrawer } from "./LichSuDrawer";
import { useResponsiveSize } from "./useResponsiveSize";

export function ChartView() {
  const router = useRouter();
  const [stash, setStash] = useState<SessionStash | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const chartSize = useResponsiveSize();

  useEffect(() => {
    const s = loadStash();
    if (!s) {
      router.replace("/");
      return;
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setStash(s);
    setHydrated(true);
  }, [router]);

  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [selectedSao, setSelectedSao] = useState<string | null>(null);
  const [openOverlay, setOpenOverlay] = useState<OverlayKind>(null);
  const [extraMessages, setExtraMessages] = useState<Msg[]>([]);
  const [viewYear, setViewYear] = useState(DEFAULT_VIEW_YEAR);
  const [viewYearLabel, setViewYearLabel] = useState(formatViewYearLabel(DEFAULT_VIEW_YEAR));
  const [saoLuuPendingYear, setSaoLuuPendingYear] = useState<number | null>(null);
  const [saoLuuError, setSaoLuuError] = useState<string | null>(null);
  const chat = useStreamChat();
  const abortRef = useRef<AbortController | null>(null);

  useEffect(
    () => () => {
      abortRef.current?.abort();
    },
    [],
  );

  const messages = extraMessages;

  useEffect(() => {
    if (!stash?.ownerId || !stash.sessionId) return;

    let cancelled = false;
    void getChatSession({
      ownerId: stash.ownerId,
      sessionId: stash.sessionId,
    })
      .then((session) => {
        if (cancelled) return;
        setExtraMessages(session.messages.map(chatMessageFromPayload));
      })
      .catch(() => {
        if (!cancelled) setExtraMessages([]);
      });

    return () => {
      cancelled = true;
    };
  }, [stash]);

  // Esc closes overlay > sao > cung (in priority)
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key !== "Escape") return;
      if (openOverlay) {
        setOpenOverlay(null);
        return;
      }
      if (selectedSao) {
        setSelectedSao(null);
        return;
      }
      if (selectedRole) {
        setSelectedRole(null);
        return;
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openOverlay, selectedSao, selectedRole]);

  const onCungClick = useCallback((role: string) => {
    setSelectedRole((prev) => (prev === role ? null : role));
  }, []);

  const onRefClick = useCallback((kind: "ref" | "sao", value: string) => {
    if (kind === "sao") {
      setSelectedSao(value);
    } else {
      setSelectedRole(value);
    }
  }, []);

  const onSend = useCallback(
    (body: string) => {
      if (!stash?.ownerId || !stash.sessionId) return;

      const aiId = `ai-${Date.now()}`;
      setExtraMessages((prev) => [
        ...prev,
        { id: `me-${Date.now()}`, sender: "me", body },
        { id: aiId, sender: "ai", body: "", toolCalls: [], streaming: true },
      ]);

      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;

      const updateAi = (mut: (msg: Msg) => Msg) => {
        setExtraMessages((prev) =>
          prev.map((m) => (m.id === aiId ? mut(m) : m)),
        );
      };

      chat.mutate(
        {
          message: body,
          ownerId: stash.ownerId,
          sessionId: stash.sessionId,
          signal: ctrl.signal,
          onEvent: (event) => {
            switch (event.type) {
              case "ids":
              case "duplicate_in_progress":
                break;
              case "text":
                updateAi((m) => ({ ...m, body: m.body + event.delta }));
                break;
              case "tool_call": {
                const entry: ChatToolEntry = {
                  id: event.id,
                  name: event.name,
                  arguments: event.arguments,
                };
                updateAi((m) => {
                  const existing = m.toolCalls ?? [];
                  const idx = existing.findIndex((t) => t.id === entry.id);
                  const next = idx >= 0
                    ? existing.map((t, i) => (i === idx ? { ...t, ...entry } : t))
                    : [...existing, entry];
                  return { ...m, toolCalls: next };
                });
                break;
              }
              case "tool_result":
                updateAi((m) => ({
                  ...m,
                  toolCalls: (m.toolCalls ?? []).map((t) =>
                    t.id === event.id ? { ...t, result: event.content } : t,
                  ),
                }));
                break;
              case "error":
                updateAi((m) => ({
                  ...m,
                  body: m.body + `\n\n_Thầy đang bận: ${event.message}_`,
                }));
                break;
              case "done":
                updateAi((m) => ({ ...m, streaming: false }));
                break;
              default:
                break;
            }
          },
        },
        {
          onSettled: () => {
            updateAi((m) => ({ ...m, streaming: false }));
          },
          onError: (err) => {
            if (ctrl.signal.aborted) return;
            updateAi((m) => ({
              ...m,
              body:
                m.body +
                `\n\n_Lỗi kết nối: ${err instanceof Error ? err.message : "không rõ"}_`,
            }));
          },
        },
      );
    },
    [chat, stash],
  );

  const onChipClick = useCallback(
    (chip: string) => {
      onSend(chip);
    },
    [onSend],
  );

  const onSessionChange = useCallback((next: SessionStash) => {
    saveStash(next);
    setStash(next);
    setExtraMessages([]);
    setViewYear(DEFAULT_VIEW_YEAR);
    setViewYearLabel(formatViewYearLabel(DEFAULT_VIEW_YEAR));
    setSaoLuuError(null);
  }, []);

  const onCurrentDeleted = useCallback(() => {
    clearStash();
    setExtraMessages([]);
    setStash(null);
    router.replace("/");
  }, [router]);

  const onSelectViewYear = useCallback(
    async (year: number) => {
      if (!stash || saoLuuPendingYear != null || year < VIEW_YEAR_MIN || year > VIEW_YEAR_MAX) return;

      setSaoLuuPendingYear(year);
      setSaoLuuError(null);
      try {
        const birthInfo = buildRequestFromProfile(stash.profile);
        const overlay = await buildSaoLuu({
          birth_info: birthInfo,
          observation_time: {
            day: 1,
            month: 1,
            year,
            hour: 0,
            gender: birthInfo.gender,
          },
        });
        setStash((current) =>
          current
            ? {
                ...current,
                laso: withSaoLuuOverlay(current.laso, overlay),
              }
            : current,
        );
        setViewYear(year);
        setViewYearLabel(formatViewYearLabel(year));
      } catch (err) {
        setSaoLuuError(err instanceof Error ? err.message : "Không đổi được năm xem");
      } finally {
        setSaoLuuPendingYear(null);
      }
    },
    [saoLuuPendingYear, stash],
  );

  const onPreviousYear = useCallback(() => {
    void onSelectViewYear(viewYear - 1);
  }, [onSelectViewYear, viewYear]);

  const onNextYear = useCallback(() => {
    void onSelectViewYear(viewYear + 1);
  }, [onSelectViewYear, viewYear]);

  if (!hydrated || !stash) {
    return (
      <div className="paper-tex min-h-screen flex items-center justify-center text-[var(--color-ink-3)] font-serif italic text-[18px]">
        Đang mở lá số của con…
      </div>
    );
  }

  const { laso, profile } = stash;
  const selectedCung: CungPayload | null = selectedRole
    ? Object.values(laso.cung_by_position).find((c) => c.role === selectedRole) ?? null
    : null;

  return (
    <div className="paper-tex h-dvh flex flex-col overflow-hidden">
      <TopBar
        breadcrumb={
          <>
            <span>{profile.name || "Giấu tên"}, {profile.year}</span>
            <span className="text-[var(--color-ink-4)]"></span>
          </>
        }
        rightActions={<TopBarMenu onOpenLichSu={() => setOpenOverlay("lichSu")} />}
      />

      <div className="flex-1 grid grid-cols-1 xl:grid-cols-[720px_1fr_320px] gap-6 xl:gap-8 px-4 sm:px-6 xl:px-9 py-5 xl:py-7 min-h-0">
        <LeftRail
          laso={laso}
          profile={profile}
          size={chartSize}
          highlightedRole={selectedRole}
          tieuVanPosition={diaChiForYear(viewYear)}
          viewYear={viewYear}
          viewYearLabel={viewYearLabel}
          yearChangePending={saoLuuPendingYear != null}
          onCungClick={onCungClick}
          onOpenDaiVan={() => setOpenOverlay("daiVan")}
          onPreviousYear={onPreviousYear}
          onNextYear={onNextYear}
        />
        <div className="min-h-[60vh] xl:min-h-0 min-w-0 h-full">
          <ChatPanel
            messages={messages}
            onSend={onSend}
            onRefClick={onRefClick}
            onChipClick={onChipClick}
            pending={chat.isPending}
          />
        </div>
        <RightRail
          selectedCung={selectedCung}
          selectedSao={selectedSao}
          onCloseCung={() => setSelectedRole(null)}
          onCloseSao={() => setSelectedSao(null)}
          onSaoClick={(name) => setSelectedSao(name)}
        />
      </div>

      {openOverlay === "daiVan" && (
        <DaiVanModal
          selectedYear={viewYear}
          pendingYear={saoLuuPendingYear}
          error={saoLuuError}
          onSelectYear={(year) => void onSelectViewYear(year)}
          onClose={() => setOpenOverlay(null)}
        />
      )}
      {openOverlay === "lichSu" && (
        <LichSuDrawer
          stash={stash}
          onSessionChange={onSessionChange}
          onCurrentDeleted={onCurrentDeleted}
          onClose={() => setOpenOverlay(null)}
        />
      )}
    </div>
  );
}

function chatMessageFromPayload(message: ChatMessagePayload): Msg {
  return {
    id: message.id,
    sender: roleToSender(message.role),
    body: message.content,
  };
}

function roleToSender(role: ChatMessageRole): Msg["sender"] {
  return role === "user" ? "me" : "ai";
}
