import type { CungPayload } from "../_lib/types";
import { classifyPhuTinh } from "../_lib/sao-classify";
import { deriveStars } from "../_lib/cung-derive";
import { colorForStarName, colorForElement } from "../_lib/ngu-hanh";

function abbrevStatus(s: string): string {
  return s.replace(/\(([^)]+)\)/, (_, content) => {
    const trimmed = content.trim();
    return trimmed.length > 0 ? `(${trimmed[0]})` : "";
  });
}

interface CungBoxProps {
  cung: CungPayload;
  highlighted?: boolean;
  tieuVan?: boolean;
  cellSize: number;
  onClick?: () => void;
}

export function CungBox({ cung, highlighted, tieuVan, cellSize, onClick }: CungBoxProps) {
  const tight = cellSize < 100;
  const veryTight = cellSize < 85;
  const maxCat = veryTight ? 1 : 2;
  const maxHung = veryTight ? 1 : 2;

  const { fixed, luu } = deriveStars(cung);
  const fixedCat = fixed.filter((s) => classifyPhuTinh(s.name) === "cat").slice(0, maxCat);
  const fixedHung = fixed.filter((s) => classifyPhuTinh(s.name) === "hung").slice(0, maxHung);
  const luuCat = luu.filter((s) => classifyPhuTinh(s.name) === "cat").slice(0, maxCat);
  const luuHung = luu.filter((s) => classifyPhuTinh(s.name) === "hung").slice(0, maxHung);

  const padding = veryTight ? "px-1.5 pt-1 pb-3" : tight ? "px-1.5 pt-1.5 pb-4" : "px-2.5 pt-2.5 pb-[18px]";
  const ringClass = highlighted
    ? "outline outline-[1.5px] -outline-offset-[1px] outline-[var(--color-crimson)]"
    : "";
  const ringShadow = highlighted ? "0 0 0 4px rgba(139,42,31,0.06)" : "none";
  const bg = highlighted
    ? "rgba(255,252,245,1)"
    : tieuVan
      ? "rgba(168,133,74,0.10)"
      : "rgba(255,252,245,0.4)";

  return (
    <div
      onClick={onClick}
      className={`relative h-full box-border border border-[rgba(26,22,17,0.14)] flex flex-col gap-px text-[11px] text-[var(--color-ink-2)] cursor-pointer transition-[background,outline] duration-200 hover:bg-[rgba(255,252,245,0.85)] overflow-hidden ${padding} ${ringClass}`}
      style={{ background: bg, boxShadow: ringShadow, zIndex: highlighted ? 2 : "auto" }}
    >
      {/* Top row: địa chi left, role centered */}
      <div className="relative w-full">
        <span className={`absolute left-0 top-0 font-serif italic text-[var(--color-ink-3)] tracking-[0.4px] leading-[1] ${veryTight ? "text-[9px]" : tight ? "text-[10px]" : "text-[11px]"}`}>
          {cung.position}
        </span>
        <div className={`text-center font-serif font-semibold tracking-[0.4px] text-[var(--color-ink)] leading-[1.05] whitespace-nowrap ${veryTight ? "text-[10px]" : tight ? "text-[12px]" : "text-[14px]"}`}>
          {cung.role === "Mệnh" && <span className="text-[var(--color-crimson)] mr-1">✦</span>}
          {cung.is_cung_than && cung.role !== "Mệnh" && (
            <span className="text-[var(--color-gold)] mr-1">✦</span>
          )}
          {cung.role ?? ""}
        </div>
      </div>

      <div
        className={`text-center font-serif font-semibold tracking-[0.2px] flex flex-col gap-px leading-[1.15] mt-0.5 ${veryTight ? "text-[11.5px]" : tight ? "text-[13px]" : "text-[15px]"}`}
        style={{ minHeight: "calc(2 * 1.15em)" }}
      >
        {cung.chinh_tinh.length > 0 && (
          cung.chinh_tinh.map((s) => (
            <div key={`ct-${s}`} style={{ color: colorForStarName(s) }}>{abbrevStatus(s)}</div>
          ))
        )}
      </div>

      {!veryTight && (
        <div className={`mt-0.5 ${tight ? "text-[9.5px]" : "text-[10.5px]"}`}>
          <div className="grid grid-cols-2 gap-x-2 tracking-[0.2px]">
            <div className="flex flex-col gap-px">
              {fixedCat.map((s) => <span key={`fc-${s.name}`} style={{ color: colorForElement(s.element) }}>{s.name}</span>)}
              {luuCat.map((s) => <span key={`lc-${s.name}`} style={{ color: colorForElement(s.element) }}>L.{s.name}</span>)}
            </div>
            <div className="flex flex-col gap-px items-end text-right">
              {fixedHung.map((s) => <span key={`fh-${s.name}`} style={{ color: colorForElement(s.element) }}>{s.name}</span>)}
              {luuHung.map((s) => <span key={`lh-${s.name}`} style={{ color: colorForElement(s.element) }}>L.{s.name}</span>)}
            </div>
          </div>

          {cung.tuhoa.length > 0 && (() => {
            const tuhoaLeft = cung.tuhoa.filter((h) => !h.includes("Kỵ"));
            const tuhoaRight = cung.tuhoa.filter((h) => h.includes("Kỵ"));
            return (
              <div className="grid grid-cols-2 gap-x-2 mt-0.5">
                <div className="flex flex-col gap-px">
                  {tuhoaLeft.map((h) => (
                    <span key={`th-l-${h}`} className="font-semibold" style={{ color: colorForStarName(h) }}>{h}</span>
                  ))}
                </div>
                <div className="flex flex-col gap-px items-end text-right">
                  {tuhoaRight.map((h) => (
                    <span key={`th-r-${h}`} className="font-semibold" style={{ color: colorForStarName(h) }}>{h}</span>
                  ))}
                </div>
              </div>
            );
          })()}
        </div>
      )}

      <div
        className={`absolute flex justify-between text-[var(--color-ink-4)] tracking-[0.4px] ${veryTight ? "text-[8px]" : tight ? "text-[9px]" : "text-[9.5px]"}`}
        style={{
          bottom: veryTight ? 3 : 4,
          left: veryTight ? 5 : tight ? 6 : 9,
          right: veryTight ? 5 : tight ? 6 : 9,
        }}
      >
        <span>{cung.age_daivan != null ? `${cung.age_daivan}` : "—"}</span>
      </div>
    </div>
  );
}
