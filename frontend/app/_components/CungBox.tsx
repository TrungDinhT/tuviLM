import type { CungPayload } from "../_lib/types";
import { classifyPhuTinh } from "../_lib/sao-classify";
import { deriveStars } from "../_lib/cung-derive";
import { colorForElement, colorForStarName } from "../_lib/ngu-hanh";

interface CungBoxProps {
  cung: CungPayload;
  highlighted?: boolean;
  tieuVan?: boolean;
  onClick?: () => void;
}

function abbrevStatus(s: string): string {
  return s.replace(/\(([^)]+)\)/, (_, content) => {
    const trimmed = content.trim();
    return trimmed.length > 0 ? `(${trimmed[0]})` : "";
  });
}

export function CungBox({ cung, highlighted, tieuVan, onClick }: CungBoxProps) {
  const { fixed, luu } = deriveStars(cung);
  const fixedCat = fixed.filter((s) => classifyPhuTinh(s.name) === "cat");
  const fixedHung = fixed.filter((s) => classifyPhuTinh(s.name) === "hung");
  const luuCat = luu.filter((s) => classifyPhuTinh(s.name) === "cat");
  const luuHung = luu.filter((s) => classifyPhuTinh(s.name) === "hung");

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
      className={`relative h-full box-border border border-[rgba(26,22,17,0.14)] flex flex-col gap-px text-[8px] sm:text-[9px] md:text-[10.5px] text-[var(--color-ink-2)] cursor-pointer transition-[background,outline] duration-200 hover:bg-[rgba(255,252,245,0.85)] overflow-hidden px-1 pt-0.5 pb-2.5 md:px-1.5 md:pt-1.5 md:pb-3 lg:px-2.5 lg:pt-2.5 lg:pb-[18px] ${ringClass}`}
      style={{ background: bg, boxShadow: ringShadow, zIndex: highlighted ? 2 : "auto" }}
    >
      {/* Header: position absolute top-left + role centered */}
      <div className="relative w-full">
        <span className="absolute left-0 top-0 font-serif italic text-[var(--color-ink-3)] tracking-[0.4px] leading-[1] text-[7px] sm:text-[8px] md:text-[9px] lg:text-[10px] xl:text-[12px]">
          {cung.position}
        </span>
        <div className="text-center pt-2.5 md:pt-3 font-serif font-semibold tracking-[0.4px] text-[var(--color-ink)] leading-[1.05] whitespace-nowrap text-[7.5px] sm:text-[8.5px] md:text-[9.5px] lg:text-[10.5px] xl:text-[12.5px]">
          {cung.role === "Mệnh" && <span className="text-[var(--color-crimson)] mr-1">✦</span>}
          {cung.is_cung_than && cung.role !== "Mệnh" && (
            <span className="text-[var(--color-gold)] mr-1">✦</span>
          )}
          {cung.role ?? ""}
        </div>
      </div>

      {/* Chính tinh */}
      <div
        className="text-center font-serif font-semibold tracking-[0.2px] flex flex-col gap-px leading-[1.15] mt-0.5 text-[7.5px] sm:text-[8.5px] md:text-[11px] lg:text-[12px] xl:text-[14px]"
        style={{ minHeight: "calc(2 * 1.15em)" }}
      >
        {cung.chinh_tinh.length > 0 ? (
          cung.chinh_tinh.map((s) => (
            <div key={`ct-${s}`} className="whitespace-nowrap" style={{ color: colorForStarName(s) }}>{abbrevStatus(s)}</div>
          ))
        ) : (
          <div className="font-serif italic text-[var(--color-ink-4)] text-[8px] md:text-[10px] lg:text-[11.5px]">
            vô chính diệu
          </div>
        )}
      </div>

      {/* Phụ tinh + Tứ Hóa: single 2-col grid so tứ hóa flows directly after lưu in each column */}
      {(() => {
        const tuhoaLeft = cung.tuhoa.filter((h) => !h.display.includes("Kỵ"));
        const tuhoaRight = cung.tuhoa.filter((h) => h.display.includes("Kỵ"));
        return (
          <div className="mt-0.5 text-[5px] sm:text-[6.5px] md:text-[7.5px] lg:text-[9.5px]">
            <div className="grid grid-cols-2 gap-x-1 md:gap-x-2 tracking-[0.2px]">
              <div className="flex flex-col gap-px">
                {fixedCat.map((s) => (
                  <span key={`fc-${s.name}`} style={{ color: colorForElement(s.element) }}>{s.name}</span>
                ))}
                {tuhoaLeft.map((h) => (
                  <span key={`th-l-${h.name}`} className="font-semibold" style={{ color: colorForElement(h.element) }}>{h.display}</span>
                ))}
                {luuCat.map((s) => (
                  <span key={`lc-${s.name}`} style={{ color: colorForElement(s.element) }}>L.{s.name}</span>
                ))}
              </div>
              <div className="flex flex-col gap-px items-end text-right">
                {fixedHung.map((s) => (
                  <span key={`fh-${s.name}`} style={{ color: colorForElement(s.element) }}>{s.name}</span>
                ))}
                {tuhoaRight.map((h) => (
                  <span key={`th-r-${h.name}`} className="font-semibold" style={{ color: colorForElement(h.element) }}>{h.display}</span>
                ))}
                {luuHung.map((s) => (
                  <span key={`lh-${s.name}`} style={{ color: colorForElement(s.element) }}>L.{s.name}</span>
                ))}
              </div>
            </div>
          </div>
        );
      })()}

      {/* Footer: age_daivan */}
      <div
        className="absolute flex justify-between text-[var(--color-ink-4)] tracking-[0.4px] text-[7px] md:text-[8.5px] lg:text-[9.5px]"
        style={{
          bottom: 3,
          left: 5,
          right: 5,
        }}
      >
        <span>{cung.age_daivan != null ? `${cung.age_daivan}` : "—"}</span>
        {cung.role === "Mệnh" && <span>· chủ</span>}
      </div>
    </div>
  );
}
