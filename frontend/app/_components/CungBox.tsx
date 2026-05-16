import type { CungPayload } from "../_lib/types";
import { classifyPhuTinh, stripHoa, stripParen } from "../_lib/sao-classify";

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

  const cat = cung.phu_tinh.filter((s) => classifyPhuTinh(s.name) === "cat").slice(0, maxCat);
  const hung = cung.phu_tinh.filter((s) => classifyPhuTinh(s.name) === "hung").slice(0, maxHung);

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
      {tieuVan && !veryTight && (
        <div
          className="absolute -top-1.5 -right-1.5 z-[3] text-[9px] font-semibold tracking-[0.5px] px-1.5 py-px rounded-lg text-white"
          style={{ background: "var(--color-gold)", boxShadow: "0 2px 6px rgba(168,133,74,0.4)" }}
        >
          2026
        </div>
      )}
      <div className="flex justify-between items-baseline gap-1 mb-px">
        <div className={`font-serif font-semibold tracking-[0.4px] text-[var(--color-ink)] leading-[1.05] pr-1 flex-1 min-w-0 ${veryTight ? "text-[10.5px]" : tight ? "text-[11.5px]" : "text-[13px]"}`}>
          {cung.role === "Mệnh" && <span className="text-[var(--color-crimson)] text-[12px] mr-1">✦</span>}
          {cung.is_cung_than && cung.role !== "Mệnh" && (
            <span className="text-[var(--color-gold)] text-[10px] mr-1">✦</span>
          )}
          {cung.role ?? ""}
        </div>
        <div className={`font-serif italic text-[var(--color-ink-3)] tracking-[0.4px] flex-none ${veryTight ? "text-[9px]" : tight ? "text-[10px]" : "text-[11px]"}`}>
          {cung.position}
        </div>
      </div>

      {cung.chinh_tinh.length > 0 ? (
        <div className={`font-serif font-semibold leading-[1.15] tracking-[0.2px] text-[var(--color-crimson)] ${veryTight ? "text-[10px]" : tight ? "text-[11px]" : "text-[12.5px]"}`}>
          {veryTight ? stripParen(cung.chinh_tinh[0]) : cung.chinh_tinh.join(" · ")}
        </div>
      ) : (
        <div className={`font-serif italic text-[var(--color-ink-4)] ${veryTight ? "text-[9.5px]" : tight ? "text-[10px]" : "text-[11.5px]"}`}>
          vô chính diệu
        </div>
      )}

      {!veryTight && (
        <div className={`flex flex-wrap tracking-[0.2px] mt-0.5 ${tight ? "text-[9.5px] gap-x-1.5 gap-y-0.5" : "text-[10.5px] gap-x-2 gap-y-0.5"}`}>
          {cat.map((s) => <span key={`cat-${s.name}`} className="text-[var(--color-jade)]">{s.name}</span>)}
          {hung.map((s) => <span key={`hung-${s.name}`} className="text-[var(--color-ink-2)]">{s.name}</span>)}
          {cung.tuhoa.map((h) => (
            <span key={`tuhoa-${h}`} className="text-[var(--color-gold)] font-semibold">Hoá {stripHoa(h)}</span>
          ))}
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
        {cung.role === "Mệnh" && !veryTight && <span>· chủ</span>}
      </div>
    </div>
  );
}
