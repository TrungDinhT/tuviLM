import { getSaoDetail } from "../_data/mock-stars";
import { Eyebrow } from "./Eyebrow";
import { Chip } from "./Buttons";

interface SaoDetailCardProps {
  saoName: string;
  onClose: () => void;
}

export function SaoDetailCard({ saoName, onClose }: SaoDetailCardProps) {
  const sao = getSaoDetail(saoName);
  return (
    <div className="absolute inset-0 flex items-stretch">
      <div
        className="absolute inset-0 bg-[rgba(244,237,224,0.7)] anim-fade-in"
        style={{ backdropFilter: "blur(2px)" }}
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="sao-detail-title"
        className="relative w-full bg-[rgba(255,252,245,0.98)] border border-[var(--color-ink-3)] p-5 overflow-auto anim-slide-right"
        style={{ boxShadow: "0 1px 0 rgba(26,22,17,0.08), 0 12px 32px rgba(26,22,17,0.10)" }}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3.5 text-[14px] text-[var(--color-ink-3)] cursor-pointer hover:text-[var(--color-crimson)]"
          aria-label="Đóng"
          type="button"
        >
          ✕
        </button>
        <Eyebrow>★ Chi tiết sao</Eyebrow>
        <h2 id="sao-detail-title" className="font-serif text-[36px] font-medium mt-1.5 mb-1 tracking-[-0.3px]">{sao.name}</h2>
        {(sao.chinese || sao.epithet) && (
          <div className="font-serif italic text-[14px] text-[var(--color-ink-3)]">
            {sao.chinese && <span>{sao.chinese} </span>}
            {sao.epithet && <span>· {sao.epithet}</span>}
          </div>
        )}

        <div className="flex gap-1.5 mt-3.5 flex-wrap">
          {sao.tags.map((t, i) => (
            <Chip key={`tag-${t}`} variant={i === 0 ? "active" : "default"} className="text-[11px]">{t}</Chip>
          ))}
        </div>

        <hr className="border-t border-[rgba(26,22,17,0.14)] my-4" />

        <div className="text-[13.5px] leading-[1.6] text-[var(--color-ink-2)] whitespace-pre-wrap">
          {sao.body}
        </div>

        <hr className="border-t border-[rgba(26,22,17,0.14)] my-4" />

        <Eyebrow style={{ fontSize: 10 }}>Hỏi sâu</Eyebrow>
        <div className="flex flex-col gap-1.5 mt-1.5">
          {sao.followUp.map((q) => (
            <Chip key={`fu-${q}`} className="justify-start">{q}</Chip>
          ))}
        </div>
      </div>
    </div>
  );
}
