"use client";

import { useEffect, useState, useCallback, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import type {
  ChatMessage as Msg,
  CungPayload,
  OverlayKind,
  SessionStash,
} from "../_lib/types";
import { loadStash } from "../_lib/session-store";
import { seedOpeningMessage, pickCannedReply } from "../_data/mock-chat";
import { TopBar } from "./TopBar";
import { Btn } from "./Buttons";
import { LeftRail } from "./LeftRail";
import { ChatPanel } from "./ChatPanel";
import { RightRail } from "./RightRail";
import { DaiVanModal } from "./DaiVanModal";
import { LichSuDrawer } from "./LichSuDrawer";
import { useResponsiveSize } from "./useResponsiveSize";

// 2026 = Bính Ngọ → tiểu vận badge sits on cung at địa chi "Ngọ"
const TIEU_VAN_POSITION = "Ngọ";

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
  const [pending, setPending] = useState(false);
  const [replySeed, setReplySeed] = useState(0);
  const timerRef = useRef<number | null>(null);

  useEffect(
    () => () => {
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
    },
    [],
  );

  const openingMessages = useMemo<Msg[]>(
    () => (stash ? seedOpeningMessage(stash.laso) : []),
    [stash],
  );
  const messages = useMemo<Msg[]>(
    () => [...openingMessages, ...extraMessages],
    [openingMessages, extraMessages],
  );

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
      setExtraMessages((prev) => [
        ...prev,
        { id: `me-${Date.now()}`, sender: "me", body },
      ]);
      const seed = replySeed;
      setReplySeed((s) => s + 1);
      setPending(true);
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
      timerRef.current = window.setTimeout(() => {
        timerRef.current = null;
        setExtraMessages((prev) => [...prev, pickCannedReply(seed)]);
        setPending(false);
      }, 600);
    },
    [replySeed],
  );

  const onChipClick = useCallback(
    (chip: string) => {
      onSend(chip);
    },
    [onSend],
  );

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
    <div className="paper-tex min-h-screen flex flex-col">
      <TopBar
        breadcrumb={
          <>
            <span>{profile.name || "Giấu tên"}, {profile.year}</span>
            <span className="text-[var(--color-ink-4)]"></span>
          </>
        }
        rightActions={
          <>
            <Btn variant="ghost" onClick={() => setOpenOverlay("lichSu")}>Lịch sử</Btn>
            <Btn variant="ghost">↗ chia sẻ</Btn>
            <Btn>⬇ tải lá số</Btn>
          </>
        }
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
        <div className="min-h-[60vh] xl:min-h-0 min-w-0">
          <ChatPanel
            messages={messages}
            onSend={onSend}
            onRefClick={onRefClick}
            onChipClick={onChipClick}
            pending={pending}
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
      {openOverlay === "lichSu" && <LichSuDrawer onClose={() => setOpenOverlay(null)} />}
    </div>
  );
}
