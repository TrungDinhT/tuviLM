"use client";

import { Pill } from "@/components/primitives/pill";
import { useRecastGuard } from "@/components/shell/recast-guard";
import { useChartStore } from "@/store/chart-store";
import { usePreferencesStore } from "@/store/preferences-store";

/**
 * Scaffolding, not product. Casting a chart is the An sao screen's job; this
 * flips the flag directly so the navigation lock, the re-cast confirmation and
 * the mute preference can be exercised before that screen exists. Delete
 * alongside the rest of `_demo/`.
 */
export function ChartLockDemo() {
  const hasChart = useChartStore((state) => state.hasChart);
  const castChart = useChartStore((state) => state.castChart);
  const muted = usePreferencesStore((state) => state.muteBirthConfirm);
  const setMuted = usePreferencesStore((state) => state.setMuteBirthConfirm);
  const { requestRecast, confirmDialog } = useRecastGuard();

  return (
    <section className="mt-8">
      <h2 className="font-display text-xl font-semibold">Khoá điều hướng</h2>
      <p className="mt-1 text-[13px] text-muted">
        Hiện tại: <b className="text-ink">{hasChart ? "đã an sao" : "chưa an sao"}</b>. Bốn tab cần
        lá số {hasChart ? "đang mở" : "đang khoá"}.
      </p>

      <div className="mt-3 flex flex-wrap gap-2">
        <Pill
          variant="ghost"
          className="px-4 py-2 text-[12px]"
          onClick={() => castChart({ stars: ["tuvi"] })}
        >
          An sao (Tử Vi)
        </Pill>
        <Pill variant="ghost" className="px-4 py-2 text-[12px]" onClick={requestRecast}>
          Về An sao
        </Pill>
      </div>

      <label className="mt-4 inline-flex cursor-pointer items-center gap-[9px] text-[13px] text-muted select-none">
        <input
          type="checkbox"
          checked={muted}
          onChange={(event) => setMuted(event.target.checked)}
          className="size-[17px] flex-none cursor-pointer accent-[var(--accent)]"
        />
        <span>
          Không nhắc lại khi xác nhận ngày sinh —{" "}
          <b className="text-ink">{muted ? "đang tắt nhắc" : "vẫn nhắc"}</b>
        </span>
      </label>

      {confirmDialog}
    </section>
  );
}
