import { Eyebrow } from "./Eyebrow";

export function DefaultPanels() {
  return (
    <div className="flex flex-col gap-4 h-full">
      <div className="bg-[rgba(255,252,245,0.7)] border border-[rgba(26,22,17,0.14)] p-4 flex flex-col gap-2.5">
        <Eyebrow className="!text-[14px] sm:!text-[15px] md:!text-[16px] lg:!text-[17px] xl:!text-[18px]">Mẹo dùng</Eyebrow>
        <div className="text-[13px] sm:text-[14px] md:text-[15px] lg:text-[16px] xl:text-[17px] text-[var(--color-ink-2)] leading-[1.55]">
          Click <b className="text-[var(--color-crimson)]">một cung</b> trên lá số → thầy giải cung đó.<br /><br />
          Click <b className="text-[var(--color-ink-2)]">một sao</b> (chữ nâu/đỏ) → thầy giảng nghĩa sao.
        </div>
      </div>
      <div className="border border-[var(--color-crimson)] p-4 flex flex-col gap-2.5" style={{ background: "rgba(139,42,31,0.06)" }}>
        <Eyebrow className="!text-[14px] sm:!text-[15px] md:!text-[16px] lg:!text-[17px] xl:!text-[18px]">Lá số nổi bật</Eyebrow>
        <div className="font-serif text-[14px] sm:text-[15px] md:text-[16px] lg:text-[17px] xl:text-[18px] leading-[1.2] text-[var(--color-ink)]">
          Mệnh có cách <i className="text-[var(--color-crimson)] italic">&quot;Tử Phủ đồng cung&quot;</i> — quý cách hiếm gặp.
        </div>
        <button type="button" className="text-[12px] text-[var(--color-crimson)] md:text-[13px] lg:text-[14px] xl:text-[15px] cursor-pointer text-left underline-offset-2 hover:underline self-start">↳ Hỏi thầy về cách này</button>
      </div>
      <div className="mt-auto text-[11px] text-[var(--color-ink-3)] leading-[1.5]">
        Diễn giải bởi AI — chỉ mang tính tham khảo, không thay thế thầy có nghề.
      </div>
    </div>
  );
}
