import type { CungPayload } from "../_lib/types";
import { classifyPhuTinh, stripHoa, stripParen } from "../_lib/sao-classify";
import { Eyebrow } from "./Eyebrow";

interface CungDetailCardProps {
  cung: CungPayload;
  onSaoClick: (saoName: string) => void;
  onClose: () => void;
}

export function CungDetailCard({ cung, onSaoClick, onClose }: CungDetailCardProps) {
  const cat = cung.phu_tinh.filter((s) => classifyPhuTinh(s.name) === "cat");
  const hung = cung.phu_tinh.filter((s) => classifyPhuTinh(s.name) === "hung");

  return (
    <div
      className="relative bg-[rgba(255,252,245,0.95)] border border-[rgba(26,22,17,0.32)] p-5 flex flex-col gap-3"
      style={{ boxShadow: "0 1px 0 rgba(26,22,17,0.08), 0 12px 32px rgba(26,22,17,0.06)" }}
    >
      <button
        onClick={onClose}
        className="absolute top-3 right-3.5 text-[14px] text-[var(--color-ink-3)] cursor-pointer hover:text-[var(--color-crimson)]"
        aria-label="Đóng"
        type="button"
      >
        ✕
      </button>

      <div>
        <Eyebrow>Cung tử vi</Eyebrow>
        <h2 className="font-serif text-[28px] font-medium mt-1 leading-tight tracking-[-0.3px]">
          {cung.role ?? "—"}
          <span className="text-[var(--color-ink-3)] font-serif italic text-[15px] ml-2">{cung.position}</span>
        </h2>
        <div className="flex gap-2 text-[11px] text-[var(--color-ink-3)] mt-1.5 flex-wrap">
          {cung.age_daivan != null && <span>{cung.age_daivan} tuổi (đại vận)</span>}
          {cung.trang_sinh && <span>· {cung.trang_sinh}</span>}
          {cung.is_cung_than && <span>· <span className="text-[var(--color-gold)]">Cung Thân</span></span>}
          {cung.is_tuan && <span>· Tuần</span>}
          {cung.is_triet && <span>· Triệt</span>}
        </div>
      </div>

      <hr className="border-t border-[rgba(26,22,17,0.14)] my-1" />

      <div>
        <Eyebrow style={{ fontSize: 10 }}>Chính tinh</Eyebrow>
        {cung.chinh_tinh.length > 0 ? (
          <div className="flex flex-wrap gap-x-2 gap-y-1 mt-1.5">
            {cung.chinh_tinh.map((s) => (
              <button
                key={`chinh-${s}`}
                onClick={() => onSaoClick(stripParen(s))}
                className="font-serif text-[16px] font-semibold text-[var(--color-crimson)] ref"
                type="button"
              >
                {s}
              </button>
            ))}
          </div>
        ) : (
          <div className="font-serif italic text-[15px] text-[var(--color-ink-4)] mt-1">vô chính diệu</div>
        )}
      </div>

      {cung.tuhoa.length > 0 && (
        <div>
          <Eyebrow style={{ fontSize: 10 }}>Tứ Hoá</Eyebrow>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {cung.tuhoa.map((h) => (
              <span
                key={`tuhoa-${h}`}
                className="text-[12.5px] font-semibold text-[var(--color-gold)] px-2 py-0.5 border border-[var(--color-gold)] rounded-sm"
                style={{ background: "rgba(168,133,74,0.10)" }}
              >
                Hoá {stripHoa(h)}
              </span>
            ))}
          </div>
        </div>
      )}

      {cat.length > 0 && (
        <div>
          <Eyebrow style={{ fontSize: 10 }}>Cát tinh ({cat.length})</Eyebrow>
          <div className="flex flex-wrap gap-x-2 gap-y-1 mt-1.5 text-[13px] text-[var(--color-jade)]">
            {cat.map((s) => (
              <button
                key={`cat-${s.name}`}
                onClick={() => onSaoClick(s.name)}
                className="ref-sao"
                style={{ color: "var(--color-jade)", borderBottomColor: "var(--color-jade)" }}
                type="button"
              >
                {s.display}
              </button>
            ))}
          </div>
        </div>
      )}

      {hung.length > 0 && (
        <div>
          <Eyebrow style={{ fontSize: 10 }}>Hung tinh ({hung.length})</Eyebrow>
          <div className="flex flex-wrap gap-x-2 gap-y-1 mt-1.5 text-[13px] text-[var(--color-ink-2)]">
            {hung.map((s) => (
              <button
                key={`hung-${s.name}`}
                onClick={() => onSaoClick(s.name)}
                className="ref-sao"
                type="button"
              >
                {s.display}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
