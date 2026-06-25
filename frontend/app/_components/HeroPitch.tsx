import { Eyebrow } from "./Eyebrow";

export function HeroPitch() {
  return (
    <div className="lg:pr-10">
      <Eyebrow>Phép cổ · AI phái Tử Vi</Eyebrow>
      <h1 className="font-serif text-[48px] sm:text-[56px] lg:text-[76px] leading-[1.02] font-medium mt-5 tracking-[-0.5px]">
        Lập lá số.<br />
        Hỏi <em className="italic text-[var(--color-crimson)]">Thầy Tuệ</em><br />
        mọi điều.
      </h1>
      <p className="font-serif italic text-[20px] leading-[1.5] text-[var(--color-ink-2)] mt-6 max-w-[440px]">
        An lá số Tử Vi theo phép cổ. Trò chuyện với người giải nghĩa từng cung, từng sao — như ngồi đối diện thầy bên ấm trà nóng.
      </p>
      <div className="flex gap-7 mt-9 text-[12px] text-[var(--color-ink-3)] tracking-[0.3px] flex-wrap">
        <span>✦ MIỄN PHÍ</span>
        <span>✦ NHANH</span>
        <span>✦ DỄ DÙNG</span>
      </div>
    </div>
  );
}
