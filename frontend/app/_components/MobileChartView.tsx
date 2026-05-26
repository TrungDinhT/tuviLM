"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import type { ChatMessage as Msg, ChatToolEntry, ChatMessageRole, CungPayload, SessionStash, OverlayKind } from "../_lib/types";
import { loadStash, saveStash } from "../_lib/session-store";
import { SUGGESTED_CHIPS } from "../_data/chat-suggestions";
import { useStreamChat } from "@/services/api/v1/chat/send";
import { getChatSession, type ChatMessagePayload } from "@/services/api/v1/conversation-history";
import { StickToBottom } from "use-stick-to-bottom";
import { getSaoDetail } from "../_data/mock-stars";
import { Chart } from "./Chart";
import { Chip } from "./Buttons";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { CungDetailCard } from "./CungDetailCard";
import { DaiVanModal } from "./DaiVanModal";
import { LichSuDrawer } from "./LichSuDrawer";
import { useResponsiveSize } from "./useResponsiveSize";
import { useIsMobile } from "./useIsMobile";
import { DefaultPanels } from "./DefaultPanels";

const TIEU_VAN_POSITION = "Ngọ";

function shortName(full: string): string {
  const parts = full.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "Giấu tên";
  return parts.map((p, i) => (i === parts.length - 1 ? p : `${p[0]}.`)).join("");
}

export function MobileChartView() {
  const router = useRouter();
  const [stash, setStash] = useState<SessionStash | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [selectedSao, setSelectedSao] = useState<string | null>(null);
  const [openOverlay, setOpenOverlay] = useState<OverlayKind>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [chatOpen, setChatOpen] = useState(false);
  const chat = useStreamChat();
  const pending = chat.isPending;
  const chartSize = useResponsiveSize();
  const isMobile = useIsMobile();
  const abortRef = useRef<AbortController | null>(null);

  useEffect(
    () => () => {
      abortRef.current?.abort();
    },
    [],
  );

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

  useEffect(() => {
    if (!stash?.ownerId || !stash.sessionId) return;

    let cancelled = false;
    void getChatSession({
      ownerId: stash.ownerId,
      sessionId: stash.sessionId,
    })
      .then((session) => {
        if (cancelled) return;
        setMessages(session.messages.map(chatMessageFromPayload));
      })
      .catch(() => {
        if (!cancelled) setMessages([]);
      });

    return () => {
      cancelled = true;
    };
  }, [stash]);

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
      if (chatOpen) {
        setChatOpen(false);
        return;
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openOverlay, selectedSao, selectedRole, chatOpen]);

  const onSend = useCallback(
    (body: string) => {
      if (!stash?.ownerId || !stash.sessionId) return;

      const aiId = `ai-${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        { id: `me-${Date.now()}`, sender: "me", body },
        { id: aiId, sender: "ai", body: "", toolCalls: [], streaming: true },
      ]);

      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;

      const updateAi = (mut: (msg: Msg) => Msg) => {
        setMessages((prev) => prev.map((m) => (m.id === aiId ? mut(m) : m)));
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

  const onRefClick = useCallback((kind: "ref" | "sao", value: string) => {
    if (kind === "sao") setSelectedSao(value);
    else setSelectedRole(value);
  }, []);

  const onSessionChange = useCallback((sessionId: string) => {
    setStash((current) => {
      if (!current) return current;
      const next = {
        ...current,
        sessionId,
        fetchedAt: new Date().toISOString(),
      };
      saveStash(next);
      return next;
    });
    setMessages([]);
  }, []);

  if (!hydrated || !stash) {
    return (
      <div className="paper-tex min-h-screen flex items-center justify-center text-[var(--color-ink-3)] font-serif italic text-[18px]">
        Đang mở lá số của con…
      </div>
    );
  }

  const selectedCung: CungPayload | null = selectedRole
    ? Object.values(stash.laso.cung_by_position).find((c) => c.role === selectedRole) ?? null
    : null;

  return (
    <div className="paper-tex min-h-screen flex flex-col">
      {/* Mobile top bar */}
      <div
        className="flex justify-between items-center px-4 py-2 border-b border-[rgba(26,22,17,0.14)]"
        style={{ background: "var(--color-paper)" }}
      >
        <button
          type="button"
          className="text-[12px] text-[var(--color-ink-2)] cursor-pointer bg-transparent border-0 p-0"
          onClick={() => router.push("/")}
        >
          ‹ {shortName(stash.profile.name)}
        </button>
        <div className="font-serif text-[18px] font-semibold tracking-[1px] text-[var(--color-ink)]">
          tuvi<em className="italic text-[var(--color-crimson)] ml-px">.</em>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="text-[11px] text-[var(--color-ink-2)] cursor-pointer bg-transparent border-0 p-0"
            onClick={() => setOpenOverlay("lichSu")}
          >
            Lịch sử
          </button>
          <button
            type="button"
            className="text-[12px] text-[var(--color-crimson)] font-serif italic bg-transparent border-0 p-0 cursor-pointer"
            onClick={() => setOpenOverlay("daiVan")}
          >
            2026 ▾
          </button>
        </div>
      </div>

      {/* Body: chart only on mobile, chart + tips side-by-side on tablet */}
      <div className="flex-1 overflow-auto min-h-0">
        {isMobile ? (
          <div
            className="border-b border-[rgba(26,22,17,0.14)] px-3 py-2 grid place-items-center"
            style={{ background: "rgba(255,252,245,0.4)" }}
          >
            <Chart
              laso={stash.laso}
              profile={stash.profile}
              size={chartSize}
              highlightedRole={selectedRole}
              tieuVanPosition={TIEU_VAN_POSITION}
              onCungClick={(role) => setSelectedRole((prev) => (prev === role ? null : role))}
            />
          </div>
        ) : (
          <div className="grid grid-cols-[1fr_320px] gap-6 px-4 py-4 min-h-full">
            <div
              className="grid place-items-center px-3 py-2 border border-[rgba(26,22,17,0.14)]"
              style={{ background: "rgba(255,252,245,0.4)" }}
            >
              <Chart
                laso={stash.laso}
                profile={stash.profile}
                size={chartSize}
                highlightedRole={selectedRole}
                tieuVanPosition={TIEU_VAN_POSITION}
                onCungClick={(role) => setSelectedRole((prev) => (prev === role ? null : role))}
              />
            </div>
            <div className="overflow-auto">
              <DefaultPanels />
            </div>
          </div>
        )}
      </div>

      {/* Chat FAB */}
      <button
        type="button"
        onClick={() => setChatOpen(true)}
        className="fixed bottom-5 right-5 z-30 w-14 h-14 rounded-full grid place-items-center text-[24px] text-[var(--color-paper)] border-0 cursor-pointer"
        style={{ background: "var(--color-crimson)", boxShadow: "0 8px 24px rgba(139,42,31,0.4)" }}
        aria-label="Mở chat với Thầy Tuệ"
      >
        ✎
      </button>

      {/* Chat bottom sheet */}
      {chatOpen && (
        <div className="fixed inset-0 z-30">
          <div
            className="absolute inset-0 bg-[rgba(26,22,17,0.4)] anim-fade-in"
            onClick={() => setChatOpen(false)}
          />
          <div
            role="dialog"
            aria-modal="true"
            className="absolute bottom-0 left-0 right-0 top-[10vh] flex flex-col bg-[var(--color-paper)] border-t-[1.5px] border-[var(--color-ink)] anim-slide-up"
            style={{ boxShadow: "0 -8px 24px rgba(26,22,17,0.18)" }}
          >
            <div className="flex justify-between items-center px-4 py-3 border-b border-[rgba(26,22,17,0.14)]">
              <div className="font-serif italic text-[var(--color-crimson)] text-[13px] tracking-[0.5px] uppercase font-medium">
                Thầy Tuệ
              </div>
              <button
                type="button"
                onClick={() => setChatOpen(false)}
                className="text-[16px] text-[var(--color-ink-3)] hover:text-[var(--color-crimson)] bg-transparent border-0 cursor-pointer"
                aria-label="Đóng"
              >
                ✕
              </button>
            </div>
            <StickToBottom
              className="flex-1 min-h-0 relative"
              resize="smooth"
              initial="instant"
            >
              <StickToBottom.Content className="px-4 py-3 flex flex-col gap-2.5">
                {messages.map((m) => (
                  <ChatMessage key={m.id} msg={m} onRefClick={onRefClick} />
                ))}
                {messages.length <= 1 && (
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {SUGGESTED_CHIPS.map((c) => (
                      <Chip key={`sug-${c}`} className="text-[10px] px-2 py-1" onClick={() => onSend(c)}>
                        {c}
                      </Chip>
                    ))}
                  </div>
                )}
              </StickToBottom.Content>
            </StickToBottom>
            <div
              className="px-3 py-2 border-t border-[rgba(26,22,17,0.14)]"
              style={{ background: "var(--color-paper)" }}
            >
              <ChatInput onSend={onSend} disabled={pending} />
            </div>
          </div>
        </div>
      )}

      {/* Cung bottom sheet */}
      {selectedCung && (
        <div className="fixed inset-0 z-40">
          <div
            className="absolute inset-0 bg-[rgba(26,22,17,0.4)] anim-fade-in"
            onClick={() => setSelectedRole(null)}
          />
          <div
            role="dialog"
            aria-modal="true"
            className="absolute bottom-0 left-0 right-0 max-h-[80vh] overflow-y-auto bg-[var(--color-paper)] border-t-[1.5px] border-[var(--color-ink)] anim-slide-up"
            style={{ boxShadow: "0 -8px 24px rgba(26,22,17,0.18)" }}
          >
            <div className="w-10 h-1 bg-[var(--color-ink-3)] rounded mx-auto mt-2 mb-1" />
            <CungDetailCard
              cung={selectedCung}
              onSaoClick={(name) => setSelectedSao(name)}
              onClose={() => setSelectedRole(null)}
            />
          </div>
        </div>
      )}

      {/* Sao bottom sheet (inline, not SaoDetailCard) */}
      {selectedSao && (() => {
        const sao = getSaoDetail(selectedSao);
        return (
          <div className="fixed inset-0 z-50">
            <div
              className="absolute inset-0 bg-[rgba(26,22,17,0.4)] anim-fade-in"
              onClick={() => setSelectedSao(null)}
            />
            <div
              role="dialog"
              aria-modal="true"
              aria-labelledby="mobile-sao-title"
              className="absolute bottom-0 left-0 right-0 max-h-[80vh] overflow-y-auto bg-[var(--color-paper)] border-t-[1.5px] border-[var(--color-ink)] anim-slide-up"
              style={{ boxShadow: "0 -8px 24px rgba(26,22,17,0.18)" }}
            >
              <div className="w-10 h-1 bg-[var(--color-ink-3)] rounded mx-auto mt-2 mb-1" />
              <div className="px-5 py-3 relative">
                <button
                  onClick={() => setSelectedSao(null)}
                  className="absolute top-2 right-3 text-[14px] text-[var(--color-ink-3)] hover:text-[var(--color-crimson)] bg-transparent border-0 cursor-pointer"
                  aria-label="Đóng"
                  type="button"
                >
                  ✕
                </button>
                <div className="eyebrow text-[10px]">★ Chi tiết sao</div>
                <h2
                  id="mobile-sao-title"
                  className="font-serif text-[24px] font-medium mt-1 mb-1 tracking-[-0.3px]"
                >
                  {sao.name}
                </h2>
                {(sao.chinese || sao.epithet) && (
                  <div className="font-serif italic text-[12px] text-[var(--color-ink-3)]">
                    {sao.chinese && <span>{sao.chinese} </span>}
                    {sao.epithet && <span>· {sao.epithet}</span>}
                  </div>
                )}
                <div className="flex gap-1.5 mt-2.5 flex-wrap">
                  {sao.tags.map((t, i) => (
                    <Chip
                      key={`tag-${t}`}
                      variant={i === 0 ? "active" : "default"}
                      className="text-[10px] px-2 py-0.5"
                    >
                      {t}
                    </Chip>
                  ))}
                </div>
                <hr className="border-t border-[rgba(26,22,17,0.14)] my-3" />
                <div className="text-[12.5px] leading-[1.6] text-[var(--color-ink-2)] whitespace-pre-wrap">
                  {sao.body}
                </div>
                <hr className="border-t border-[rgba(26,22,17,0.14)] my-3" />
                <div className="eyebrow text-[10px]">Hỏi sâu</div>
                <div className="flex flex-col gap-1.5 mt-1.5">
                  {sao.followUp.map((q) => (
                    <Chip key={`fu-${q}`} className="justify-start text-[11px]">
                      {q}
                    </Chip>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
      })()}

      {openOverlay === "daiVan" && <DaiVanModal onClose={() => setOpenOverlay(null)} />}
      {openOverlay === "lichSu" && (
        <LichSuDrawer
          ownerId={stash.ownerId}
          chartProfileId={stash.chartProfileId}
          currentSessionId={stash.sessionId}
          onSessionChange={onSessionChange}
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
