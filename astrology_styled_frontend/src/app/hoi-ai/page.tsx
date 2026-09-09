import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";
import { HoiAiScreen } from "@/features/hoi-ai/hoi-ai-screen";

export default function Page() {
  return (
    <ScreenPad>
      <StickyHeader
        eyebrow="Hỏi AI"
        title="Nghê Sao"
        subtitle="Tinh linh dẫn đường · luôn thành thật, luôn dịu dàng."
      />
      <HoiAiScreen />
    </ScreenPad>
  );
}
