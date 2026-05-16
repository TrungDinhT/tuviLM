import type { BuildLasoResponse, UserProfile } from "../_lib/types";
import { DIA_CHI_GRID, DIA_CHI_ORDER } from "@/constants/chart-layout";
import { CungBox } from "./CungBox";
import { ChartCenter } from "./ChartCenter";

interface ChartProps {
  laso: BuildLasoResponse;
  profile: UserProfile;
  size?: number;
  highlightedRole?: string | null;
  tieuVanPosition?: string | null;
  onCungClick?: (role: string) => void;
}

export function Chart({
  laso,
  profile,
  size = 460,
  highlightedRole,
  tieuVanPosition,
  onCungClick,
}: ChartProps) {
  const cell = size / 4;
  return (
    <div
      className="relative grid border border-[var(--color-ink-3)]"
      style={{
        width: size,
        height: size,
        gridTemplateColumns: `repeat(4, ${cell}px)`,
        gridTemplateRows: `repeat(4, ${cell}px)`,
        background: "rgba(255,252,245,0.25)",
      }}
    >
      {DIA_CHI_ORDER.map((diaChi) => {
        const cung = laso.cung_by_position[diaChi];
        const pos = DIA_CHI_GRID[diaChi];
        if (!cung || !pos) return null;
        return (
          <div
            key={diaChi}
            style={{ gridColumn: pos.c + 1, gridRow: pos.r + 1, minWidth: 0, minHeight: 0, overflow: "hidden" }}
          >
            <CungBox
              cung={cung}
              highlighted={highlightedRole != null && cung.role === highlightedRole}
              tieuVan={tieuVanPosition === diaChi}
              cellSize={cell}
              onClick={() => cung.role && onCungClick?.(cung.role)}
            />
          </div>
        );
      })}
      <div style={{ gridColumn: "2 / span 2", gridRow: "2 / span 2", minWidth: 0, minHeight: 0, overflow: "hidden" }}>
        <ChartCenter laso={laso} profile={profile} cellSize={cell} />
      </div>
    </div>
  );
}
