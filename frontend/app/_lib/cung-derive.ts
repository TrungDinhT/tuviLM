import type { CungPayload, StarPayload } from "./types";

export interface DerivedStars {
  fixed: StarPayload[];   // natal phụ tinh, deduped, excluding sao lưu
  luu: StarPayload[];     // sao lưu (transit) — deduped by name
}

export function deriveStars(cung: CungPayload): DerivedStars {
  const luuNames = new Set(cung.saoLuu.map((s) => s.name));

  const luuSeen = new Set<string>();
  const luu: StarPayload[] = [];
  for (const s of cung.saoLuu) {
    if (!luuSeen.has(s.name)) {
      luuSeen.add(s.name);
      luu.push(s);
    }
  }

  const fixedSeen = new Set<string>();
  const fixed: StarPayload[] = [];
  for (const s of cung.phu_tinh) {
    if (luuNames.has(s.name)) continue;
    if (fixedSeen.has(s.name)) continue;
    fixedSeen.add(s.name);
    fixed.push(s);
  }

  return { fixed, luu };
}
