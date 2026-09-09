import { VO_CHINH_DIEU_KEY } from "@/content/destiny";
import type { BuildLasoResponse, Cung } from "@/lib/api/schemas";
import { starKeyFromName } from "@/lib/theme";

export { VO_CHINH_DIEU_KEY };

/**
 * Pure selectors over the cast chart — the deck's only read path.
 *
 * Every key these produce is a stable table key, never a display string:
 * star names are normalised through `starKeyFromName` (trạng thái suffix
 * stripped, diacritics folded) and sorted, so a song tinh pair keys the same
 * entry whichever order the backend returns it in.
 */

function cungMenh(chart: BuildLasoResponse): Cung | undefined {
  return Object.values(chart.cung_by_position).find((cung) => cung.role === "Mệnh");
}

/** The chính tinh names of cung Mệnh, exactly as the backend names them. */
export function menhChinhTinh(chart: BuildLasoResponse): readonly string[] {
  return cungMenh(chart)?.chinh_tinh ?? [];
}

/** A star name for display: trạng thái suffix stripped, diacritics kept. */
export function displayStarName(name: string): string {
  return name.replace(/\s*\([^)]*\)\s*$/, "").trim();
}

/**
 * The deck's main-card key: the normalised chính tinh keys of cung Mệnh,
 * sorted and joined (`"tuvi"`, `"thienphu+tuvi"`). An empty Mệnh — vô chính
 * diệu — keys to its own authored entry.
 */
export function menhStarKey(chart: BuildLasoResponse): string {
  const keys = menhChinhTinh(chart).map(starKeyFromName).sort();
  return keys.length === 0 ? VO_CHINH_DIEU_KEY : keys.join("+");
}

/**
 * The role of the cung holding a given star — `"Hóa Lộc"` arrives in `tuhoa`,
 * `"Lộc Tồn"` in `phu_tinh`, so both lists are searched. Null when the star
 * is absent, which a real chart never is for these two.
 */
export function cungRoleHolding(
  chart: BuildLasoResponse,
  starName: "Hóa Lộc" | "Lộc Tồn",
): string | null {
  for (const cung of Object.values(chart.cung_by_position)) {
    if (cung.tuhoa.includes(starName)) return cung.role;
    if (cung.phu_tinh.some((sao) => sao.name === starName)) return cung.role;
  }
  return null;
}
