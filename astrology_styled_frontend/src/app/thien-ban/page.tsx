import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";

/**
 * Route stub. The shell, header and navigation are real; the screen body is
 * not built yet — see the v1 scope note in AGENTS.md. Replace this placeholder
 * when the thien-ban screen lands as its own change.
 */
export default function Page() {
  return (
    <ScreenPad>
      <StickyHeader eyebrow="Tính năng nâng cao" title="Thiên Bàn" subtitle="Sáu mảnh chủ đề rút ra từ mười hai cung của lá số." />
      <p className="text-[13.5px] text-muted">Màn hình này sẽ được dựng ở thay đổi tiếp theo.</p>
    </ScreenPad>
  );
}
