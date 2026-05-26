import type { BuildLasoResponse, UserProfile } from "../_lib/types";

interface ChartCenterProps {
  laso: BuildLasoResponse;
  profile: UserProfile;
  cellSize: number;
}

export function ChartCenter({ laso, profile, cellSize }: ChartCenterProps) {
  const tight = cellSize < 100;
  const veryTight = cellSize < 85;
  const padding = veryTight ? "px-2 py-2.5" : tight ? "px-3 py-3.5" : "px-4 py-[18px]";
  const calLabel = profile.calendar === "am" ? "Âm" : "Dương";
  const sex = profile.gender === "M" ? "♂" : "♀";

  return (
    <div
      className={`relative h-full box-border border border-[rgba(26,22,17,0.14)] flex flex-col overflow-hidden ${padding}`}
      style={{ background: "rgba(255,252,245,0.7)", gap: 2 }}
    >
      <div className={`eyebrow ${veryTight ? "!text-[10px]" : tight ? "!text-[12px]" : "!text-[15px]"} text-center`} style={{ letterSpacing: "1.4px" }}>
        lá số tử vi
      </div>
      <div className={`font-serif font-medium text-[var(--color-ink)] leading-[1.05] mt-0.5 tracking-[0.3px] ${veryTight ? "text-[13px]" : tight ? "text-[16px]" : "text-[24px]"}`}>
        {profile.name}
      </div>
      <div className={`text-[var(--color-ink-3)] leading-[1.4] mt-0.5 tracking-[0.2px] ${veryTight ? "text-[9px]" : tight ? "text-[9.5px]" : "text-[11px]"}`}>
        {veryTight
          ? `${sex} ${profile.year}`
          : <>{sex} · {profile.year}<br />{String(profile.day).padStart(2, "0")}/{String(profile.month).padStart(2, "0")} {calLabel} · {String(profile.hour).padStart(2, "0")}:{String(profile.minute).padStart(2, "0")}</>
        }
      </div>
      {!veryTight && (
        <div className={`text-[var(--color-ink-2)] leading-[1.5] ${tight ? "mt-1.5" : "mt-2.5"} ${tight ? "text-[9.5px]" : "text-[11px]"}`}>
          <div className="truncate"><span className="text-[var(--color-ink-3)]">Mã:</span> {laso.id}</div>
        </div>
      )}
      <div className={`flex justify-between mt-auto border-t border-[rgba(26,22,17,0.14)] ${veryTight ? "text-[9px] pt-1" : tight ? "text-[7.5px] pt-1.5" : "text-[9.5px] pt-2"}`}>
        <div><span className="text-[var(--color-ink-3)] mr-1.5">Năm</span><span className="text-[var(--color-crimson)] font-semibold">2026 Bính Ngọ</span></div>
        <div className="text-[var(--color-gold)]">{veryTight ? "24–33" : "Đại vận 24–33 ▾"}</div>
      </div>
    </div>
  );
}
