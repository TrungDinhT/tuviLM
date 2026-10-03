import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";

/**
 * Route stub. The shell, header and navigation are real; the screen body is
 * not built yet — see the v1 scope note in AGENTS.md. Replace this placeholder
 * when the van-han screen lands as its own change.
 */
export default function Page() {
  return (
    <ScreenPad>
      <StickyHeader eyebrow="Vận hạn 2026" title="Đường sao năm nay" subtitle="Mở từng lĩnh vực để xem tinh tú đang xoay vần thế nào." />
      <p className="text-[13.5px] text-muted">Màn hình này sẽ được dựng ở thay đổi tiếp theo.</p>
    </ScreenPad>
  );
}
