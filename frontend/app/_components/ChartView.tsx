"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import type {
  ChatMessage as Msg,
  ChatToolEntry,
  CungPayload,
  OverlayKind,
  SessionDetailResponse,
  SessionStash,
  UserProfile,
} from "../_lib/types";
import { getClientId, loadStash, saveStash } from "../_lib/session-store";
import { seedOpeningMessage } from "../_data/mock-chat";
import { useStreamChat } from "@/services/api/v1/chat/send";
import { getSessionDetail } from "@/services/api/v1/sessions";
import { TopBar } from "./TopBar";
import { TopBarMenu } from "./TopBarMenu";
import { LeftRail } from "./LeftRail";
import { ChatPanel } from "./ChatPanel";
import { RightRail } from "./RightRail";
import { DaiVanModal } from "./DaiVanModal";
import { LichSuDrawer } from "./LichSuDrawer";
import { useResponsiveSize } from "./useResponsiveSize";

const TIEU_VAN_POSITION = "Ngọ";

function stashFromDetail(detail: SessionDetailResponse): SessionStash {
  const birth = detail.chart_profile.birth_metadata;
  const profile: UserProfile = {
    name: detail.chart_profile.display_name,
    gender: birth.gender,
    calendar: birth.calendar === "solar" ? "duong" : "am",
    date: birth.date,
    month: birth.month,
    year: birth.year,
    hour: birth.hour,
    minute: birth.minute,
  };
  return { laso: detail.laso, profile, fetchedAt: new Date().toISOString() };
}

export function ChartView() {
  const router = useRouter();
  const [stash, setStash] = useState<SessionStash | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const chartSize = useResponsiveSize();
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [selectedSao, setSelectedSao] = useState<string | null>(null);
  const [openOverlay, setOpenOverlay] = useState<OverlayKind>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [activeLeafId, setActiveLeafId] = useState<string | null>(null);
  const chat = useStreamChat();
  const abortRef = useRef<AbortController | null>(null);

  const applySessionDetail = useCallback((detail: SessionDetailResponse) => {
    const nextStash = stashFromDetail(detail);
    saveStash(nextStash);
    setStash(nextStash);
    setMessages(detail.messages);
    setActiveLeafId(detail.session.active_leaf_id);
  }, []);

  useEffect(() => {
    const s = loadStash();
    if (!s) {
      router.replace("/");
      return;
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setStash(s);
    setMessages(seedOpeningMessage(s.laso));
    setActiveLeafId(s.laso.active_leaf_id);
    setHydrated(true);

    getSessionDetail(getClientId(), s.laso.session_id)
      .then(applySessionDetail)
      .catch(() => {
        // Keep cached chart usable if the persisted session cannot be loaded.
      });
  }, [applySessionDetail, router]);

  useEffect(
    () => () => {
      abortRef.current?.abort();
    },
    [],
  );

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
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openOverlay, selectedSao, selectedRole]);

  const onCungClick = useCallback((role: string) => {
    setSelectedRole((prev) => (prev === role ? null : role));
  }, []);

  const onRefClick = useCallback((kind: "ref" | "sao", value: string) => {
    if (kind === "sao") setSelectedSao(value);
    else setSelectedRole(value);
  }, []);

  const onSend = useCallback(
    (body: string) => {
      if (!stash || !activeLeafId) return;

      const userTempId = `me-${Date.now()}`;
      const aiTempId = `ai-${Date.now()}`;
      let userMessageId = userTempId;
      let assistantMessageId = aiTempId;

      setMessages((prev) => [
        ...prev,
        { id: userTempId, parent_id: activeLeafId, sender: "user", body, status: "pending" },
        {
          id: aiTempId,
          parent_id: userTempId,
          sender: "assistant",
          body: "",
          toolCalls: [],
          status: "streaming",
        },
      ]);

      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;

      const updateAi = (mut: (msg: Msg) => Msg) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantMessageId ? mut(m) : m)),
        );
      };

      chat.mutate(
        {
          clientId: getClientId(),
          sessionId: stash.laso.session_id,
          parentId: activeLeafId,
          content: body,
          signal: ctrl.signal,
          onEvent: (event) => {
            switch (event.type) {
              case "ids":
                userMessageId = event.user_message_id;
                assistantMessageId = event.assistant_message_id;
                setMessages((prev) =>
                  prev.map((m) => {
                    if (m.id === userTempId) {
                      return { ...m, id: userMessageId, status: "confirmed" };
                    }
                    if (m.id === aiTempId) {
                      return { ...m, id: assistantMessageId, parent_id: userMessageId };
                    }
                    return m;
                  }),
                );
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
              case "failed":
                updateAi((m) => ({
                  ...m,
                  body: m.body + `\n\n_Thầy đang bận: ${event.message}_`,
                  status: "failed",
                }));
                setActiveLeafId(userMessageId);
                break;
              case "done":
                updateAi((m) => ({ ...m, status: "confirmed" }));
                setActiveLeafId(assistantMessageId);
                break;
            }
          },
        },
        {
          onSettled: () => {
            updateAi((m) =>
              m.status === "streaming" ? { ...m, status: "cancelled" } : m,
            );
          },
          onError: (err) => {
            if (ctrl.signal.aborted) return;
            updateAi((m) => ({
              ...m,
              body:
                m.body +
                `\n\n_Lỗi kết nối: ${err instanceof Error ? err.message : "không rõ"}_`,
              status: "failed",
            }));
            setActiveLeafId(userMessageId);
          },
        },
      );
    },
    [activeLeafId, chat, stash],
  );

  const onChipClick = useCallback((chip: string) => onSend(chip), [onSend]);

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
          tieuVanPosition={TIEU_VAN_POSITION}
          onCungClick={onCungClick}
          onOpenDaiVan={() => setOpenOverlay("daiVan")}
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

      {openOverlay === "daiVan" && <DaiVanModal onClose={() => setOpenOverlay(null)} />}
      {openOverlay === "lichSu" && (
        <LichSuDrawer
          currentSessionId={stash.laso.session_id}
          onClose={() => setOpenOverlay(null)}
          onSelectSession={(sessionId) => {
            getSessionDetail(getClientId(), sessionId)
              .then(applySessionDetail)
              .then(() => setOpenOverlay(null));
          }}
        />
      )}
    </div>
  );
}
