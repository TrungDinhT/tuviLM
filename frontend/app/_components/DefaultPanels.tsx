import type { CauPhuResponse } from "../_lib/types";
import { CauPhuCard } from "./CauPhuCard";
import { Eyebrow } from "./Eyebrow";

interface DefaultPanelsProps {
  cauPhu?: CauPhuResponse;
}

export function DefaultPanels({ cauPhu }: DefaultPanelsProps) {
  return (
    <div className="flex flex-col gap-4 h-full">
      <div className="bg-[rgba(255,252,245,0.7)] border border-[rgba(26,22,17,0.14)] p-4 flex flex-col gap-2.5">
        <Eyebrow className="!text-[14px] sm:!text-[15px] md:!text-[16px] lg:!text-[17px] xl:!text-[18px]">Mẹo dùng</Eyebrow>
        <div className="text-[13px] sm:text-[14px] md:text-[15px] lg:text-[16px] xl:text-[17px] text-[var(--color-ink-2)] leading-[1.55]">
          Click <b className="text-[var(--color-crimson)]">một cung</b> trên lá số → thầy giải cung đó.<br /><br />
          Click <b className="text-[var(--color-ink-2)]">một sao</b> (chữ nâu/đỏ) → thầy giảng nghĩa sao.
        </div>
      </div>
      {cauPhu && <CauPhuCard cauPhu={cauPhu} />}
      <div className="mt-auto text-[11px] text-[var(--color-ink-3)] leading-[1.5]">
        Diễn giải bởi AI — chỉ mang tính tham khảo, không thay thế thầy có nghề.
      </div>
    </div>
  );
}
