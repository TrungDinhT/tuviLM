"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { SessionStash } from "../_lib/types";
import { loadStash } from "../_lib/session-store";

export function ChartViewBoot() {
  const router = useRouter();
  const [state, setState] = useState<{ stash: SessionStash | null; checked: boolean }>({
    stash: null,
    checked: false,
  });

  useEffect(() => {
    const s = loadStash();
    if (!s) {
      router.replace("/");
      return;
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect -- syncing sessionStorage (browser-only external state) into React on mount
    setState({ stash: s, checked: true });
  }, [router]);

  const { stash, checked } = state;

  if (!checked || !stash) {
    return (
      <div className="paper-tex min-h-screen flex items-center justify-center text-[var(--color-ink-3)] font-serif italic text-[18px]">
        Đang mở lá số của con…
      </div>
    );
  }

  return (
    <div className="paper-tex min-h-screen flex items-center justify-center text-[var(--color-ink-3)] font-serif italic text-[28px] flex-col gap-3">
      <div>Lá số đã sẵn sàng — {stash.profile.name || "Lần sau nhớ ghi tên vào nhé!"}</div>
      <div className="text-[13px] text-[var(--color-ink-4)] not-italic">
        ID: {stash.laso.id} · {Object.keys(stash.laso.cung_by_position).length} cung
      </div>
      <div className="text-[12px] text-[var(--color-ink-4)] not-italic">
        ChartView wiring: Task 8
      </div>
    </div>
  );
}
