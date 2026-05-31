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

type BadgePos = "top-left" | "top-center" | "top-right" | "bot-left" | "bot-center" | "bot-right";

interface TuanTrietPair {
  ids: [string, string];
  anchor: string;
  pos: BadgePos;
}

const TUAN_TRIET_PAIRS: TuanTrietPair[] = [
  { ids: ["Tý", "Sửu"], anchor: "Tý", pos: "top-left" },
  { ids: ["Thân", "Dậu"], anchor: "Thân", pos: "bot-center" },
  { ids: ["Ngọ", "Mùi"], anchor: "Ngọ", pos: "bot-right" },
  { ids: ["Thìn", "Tị"], anchor: "Thìn", pos: "top-center" },
  { ids: ["Tuất", "Hợi"], anchor: "Tuất", pos: "bot-center" },
  { ids: ["Dần", "Mão"], anchor: "Dần", pos: "top-center" },
];

function badgeOffset(pos: BadgePos, cellW: number, cellH: number, anchorGrid: { r: number; c: number }) {
  const xLeft = anchorGrid.c * cellW;
  const xCenter = anchorGrid.c * cellW + cellW / 2;
  const xRight = (anchorGrid.c + 1) * cellW;
  const yTop = anchorGrid.r * cellH;
  const yBot = (anchorGrid.r + 1) * cellH;
  switch (pos) {
    case "top-left": return { x: xLeft, y: yTop };
    case "top-center": return { x: xCenter, y: yTop };
    case "top-right": return { x: xRight, y: yTop };
    case "bot-left": return { x: xLeft, y: yBot };
    case "bot-center": return { x: xCenter, y: yBot };
    case "bot-right": return { x: xRight, y: yBot };
  }
}

export function Chart({
  laso,
  profile,
  size = 690,
  highlightedRole,
  tieuVanPosition,
  onCungClick,
}: ChartProps) {
  const cellW = size / 4;
  const cellH = cellW * 1.5;
  return (
    <div
      className="relative grid border border-[var(--color-ink-3)]"
      style={{
        width: size,
        height: cellH * 4,
        gridTemplateColumns: `repeat(4, ${cellW}px)`,
        gridTemplateRows: `repeat(4, ${cellH}px)`,
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
              onClick={() => cung.role && onCungClick?.(cung.role)}
            />
          </div>
        );
      })}
      <div style={{ gridColumn: "2 / span 2", gridRow: "2 / span 2", minWidth: 0, minHeight: 0, overflow: "hidden" }}>
        <ChartCenter laso={laso} profile={profile} cellSize={cellW} />
      </div>
      {TUAN_TRIET_PAIRS.map((pair) => {
        const c1 = laso.cung_by_position[pair.ids[0]];
        const c2 = laso.cung_by_position[pair.ids[1]];
        const hasTuan = !!(c1?.is_tuan || c2?.is_tuan);
        const hasTriet = !!(c1?.is_triet || c2?.is_triet);
        if (!hasTuan && !hasTriet) return null;
        const label = hasTuan && hasTriet ? "Tuần-Triệt" : hasTuan ? "Tuần" : "Triệt";
        const anchorGrid = DIA_CHI_GRID[pair.anchor];
        if (!anchorGrid) return null;
        const { x, y } = badgeOffset(pair.pos, cellW, cellH, anchorGrid);
        return (
          <div
            key={`tt-${pair.anchor}`}
            className="absolute z-10 px-2 py-0.5 text-[7px] sm:text-[8px] md:text-[10px] font-semibold tracking-[0.5px] uppercase rounded-sm bg-[var(--color-crimson)] text-[var(--color-paper)] whitespace-nowrap pointer-events-none"
            style={{
              left: x,
              top: y,
              transform: "translate(-50%, -50%)",
              boxShadow: "0 2px 6px rgba(26,22,17,0.3)",
            }}
          >
            {label}
          </div>
        );
      })}
      {tieuVanPosition && DIA_CHI_GRID[tieuVanPosition] && (() => {
        const g = DIA_CHI_GRID[tieuVanPosition];
        const x = g.c * cellW + cellW / 2;
        const y = (g.r + 1) * cellH - 4;
        return (
          <div
            key="tieu-van-badge"
            className="absolute z-20 px-1.5 py-0.5 text-[7px] sm:text-[8px] md:text-[10px] font-semibold tracking-[0.5px] rounded-lg whitespace-nowrap text-white pointer-events-none"
            style={{
              left: x,
              top: y,
              transform: "translate(-50%, -100%)",
              background: "var(--color-gold)",
              boxShadow: "0 2px 6px rgba(168,133,74,0.4)",
            }}
          >
            2026
          </div>
        );
      })()}
    </div>
  );
}
