import type { BuildLasoResponse, UserProfile } from "../_lib/types";
import { formatChartYearLabel, VIEW_YEAR_MAX, VIEW_YEAR_MIN } from "../_lib/sao-luu-overlay";
import { Chart } from "./Chart";
import { Btn } from "./Buttons";
import { Eyebrow } from "./Eyebrow";

interface LeftRailProps {
  laso: BuildLasoResponse;
  profile: UserProfile;
  highlightedRole: string | null;
  tieuVanPosition: string | null;
  viewYear: number;
  viewYearLabel: string;
  yearChangePending: boolean;
  onCungClick: (role: string) => void;
  onOpenDaiVan: () => void;
  onPreviousYear: () => void;
  onNextYear: () => void;
  mentions?: string[];
  size?: number;
}

export function LeftRail({
  laso,
  profile,
  highlightedRole,
  tieuVanPosition,
  viewYear,
  viewYearLabel,
  yearChangePending,
  onCungClick,
  onOpenDaiVan,
  onPreviousYear,
  onNextYear,
  mentions = [],
  size = 690,
}: LeftRailProps) {
  return (
    <div className="flex flex-col gap-[18px] items-center xl:items-start">
      <Chart
        laso={laso}
        profile={profile}
        size={size}
        highlightedRole={highlightedRole}
        tieuVanPosition={tieuVanPosition}
        tieuVanYear={viewYear}
        viewYearLabel={formatChartYearLabel(viewYear)}
        onCungClick={onCungClick}
      />
      <div className="flex items-center justify-between">
        <div>
          <Eyebrow style={{ fontSize: 10, marginBottom: 2 }}>năm xem</Eyebrow>
          <div className="font-serif text-[22px] text-[var(--color-crimson)] leading-none">{viewYearLabel}</div>
        </div>
        <div className="flex gap-1.5">
          <Btn
            variant="ghost"
            className="px-1.5 py-1.5 text-[14px]"
            disabled={yearChangePending || viewYear <= VIEW_YEAR_MIN}
            onClick={onPreviousYear}
            aria-label="Xem năm trước"
          >
            ◂
          </Btn>
          <Btn className="text-[12px]" onClick={onOpenDaiVan}>↧ đổi đại vận</Btn>
          <Btn
            variant="ghost"
            className="px-1.5 py-1.5 text-[14px]"
            disabled={yearChangePending || viewYear >= VIEW_YEAR_MAX}
            onClick={onNextYear}
            aria-label="Xem năm sau"
          >
            ▸
          </Btn>
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
