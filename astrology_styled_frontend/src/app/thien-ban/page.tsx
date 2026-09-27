import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";
import { CapabilityLauncher } from "@/features/nang-luc/nang-luc-screen";

export default function Page() {
  return (
    <ScreenPad>
      <StickyHeader
        eyebrow="Tính năng nâng cao"
        title="Thiên Bàn"
        subtitle="Khám phá những tầng sâu trong lá số của bạn."
      />
      <CapabilityLauncher />
    </ScreenPad>
  );
}
