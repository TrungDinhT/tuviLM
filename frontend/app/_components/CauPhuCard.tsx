import type { CauPhuResponse } from "../_lib/types";
import { Eyebrow } from "./Eyebrow";

interface CauPhuCardProps {
  cauPhu: CauPhuResponse;
  className?: string;
}

export function CauPhuCard({ cauPhu, className = "" }: CauPhuCardProps) {
  const lines = cauPhu.cac_cau.length > 0
    ? cauPhu.cac_cau
    : cauPhu.cau_phu.split("\n");

  return (
    <section
      aria-label="Câu Phú giới thiệu lá số"
      className={`relative overflow-hidden border border-[var(--color-crimson)] px-4 py-4 ${className}`}
      style={{
        background:
          "linear-gradient(145deg, rgba(139,42,31,0.075), rgba(168,133,74,0.045))",
      }}
    >
      <span
        aria-hidden="true"
        className="absolute -top-4 -right-2 font-serif text-[72px] leading-none text-[rgba(139,42,31,0.08)]"
      >
        文
      </span>

      <div className="relative flex items-start justify-between gap-3">
        <Eyebrow className="!text-[15px] sm:!text-[16px]">Câu Phú</Eyebrow>
        <span className="shrink-0 border border-[rgba(139,42,31,0.3)] px-2 py-0.5 text-[9px] uppercase tracking-[1px] text-[var(--color-crimson)]">
          Mệnh tại {cauPhu.vi_tri}
        </span>
      </div>

      <h2 className="relative mt-2 font-serif text-[13px] font-medium leading-[1.4] text-[var(--color-ink-2)]">
        {cauPhu.tieu_de}
      </h2>

      <div className="relative my-3 flex items-center gap-2" aria-hidden="true">
        <span className="h-px flex-1 bg-[rgba(139,42,31,0.22)]" />
        <span className="text-[10px] text-[var(--color-gold)]">◆</span>
        <span className="h-px flex-1 bg-[rgba(139,42,31,0.22)]" />
      </div>

      <blockquote className="relative m-0 text-center font-serif text-[14px] italic leading-[1.75] text-[var(--color-ink)]">
        {lines.map((line, index) => (
          <p key={`${index}-${line}`} className="m-0">
            {line}
          </p>
        ))}
      </blockquote>

      <div className="relative mt-3 text-center text-[9px] uppercase tracking-[1.1px] text-[var(--color-ink-3)]">
        {cauPhu.tuan_triet}
      </div>
    </section>
  );
}
