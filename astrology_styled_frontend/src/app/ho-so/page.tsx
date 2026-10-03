import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";
import { HoSoScreen } from "@/features/ho-so/ho-so-screen";

export default function Page() {
  return (
    <ScreenPad>
      <StickyHeader
        eyebrow="Hồ sơ"
        title="Bạn Sao Trẻ"
        subtitle="Lá số đã lưu, giao diện và nhắc nhở của bạn."
      />
      <HoSoScreen />
    </ScreenPad>
  );
}
