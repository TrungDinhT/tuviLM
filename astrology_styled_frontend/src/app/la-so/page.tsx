import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";
import { LaSoScreen } from "@/features/la-so/la-so-screen";

export default function Page() {
  return (
    <ScreenPad>
      <StickyHeader eyebrow="Lá số gốc" title="Chi tiết 12 cung" />
      <LaSoScreen />
    </ScreenPad>
  );
}
