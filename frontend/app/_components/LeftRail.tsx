import type { BuildLasoResponse, UserProfile } from "../_lib/types";
import { Chart } from "./Chart";
import { Btn } from "./Buttons";
import { Eyebrow } from "./Eyebrow";

interface LeftRailProps {
  laso: BuildLasoResponse;
  profile: UserProfile;
  highlightedRole: string | null;
  tieuVanPosition: string | null;
  onCungClick: (role: string) => void;
  onOpenDaiVan: () => void;
  mentions?: string[];
  size?: number;
}

export function LeftRail({
  laso,
  profile,
  highlightedRole,
  tieuVanPosition,
  onCungClick,
  onOpenDaiVan,
  mentions = [],
  size = 690,
}: LeftRailProps) {
  return (
    <div className="flex flex-col gap-[18px]">
      <Chart
        laso={laso}
        profile={profile}
        size={size}
        highlightedRole={highlightedRole}
        tieuVanPosition={tieuVanPosition}
        onCungClick={onCungClick}
      />
      <div className="flex items-center justify-between">
        <div>
          <Eyebrow style={{ fontSize: 10, marginBottom: 2 }}>năm xem</Eyebrow>
          <div className="font-serif text-[22px] text-[var(--color-crimson)] leading-none">Bính Ngọ · 2026</div>
        </div>
        <div className="flex gap-1.5">
          <Btn variant="ghost" className="px-1.5 py-1.5 text-[14px]" disabled title="Sắp ra mắt">◂</Btn>
          <Btn className="text-[12px]" onClick={onOpenDaiVan}>↧ đổi đại vận</Btn>
          <Btn variant="ghost" className="px-1.5 py-1.5 text-[14px]" disabled title="Sắp ra mắt">▸</Btn>
        </div>
      </div>
      {mentions.length > 0 && (
        <div className="border-l-2 border-[var(--color-crimson)] pl-3">
          <Eyebrow style={{ fontSize: 10, marginBottom: 4 }}>Thầy đang nói về</Eyebrow>
          {mentions.map((m, i) => (
            <div key={i} className="font-serif text-[15px] leading-[1.4]">
              <span className="text-[var(--color-ink-3)] text-[11px] mr-1.5">{String(i + 1).padStart(2, "0")}</span>
              {m}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
