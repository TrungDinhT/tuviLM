import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";

import { AccentDemo } from "./_demo/accent-demo";
import { ApiDemo } from "./_demo/api-demo";
import { ChartLockDemo } from "./_demo/chart-lock-demo";
import { PrimitivesDemo } from "./_demo/primitives-demo";

/**
 * Route stub for An sao. The shell around it is real; the casting machine —
 * pickers, the 12-chi clock, the constellation reward — lands as its own
 * change. Everything below the header is scaffolding for verifying the
 * foundation, and goes when the real screen arrives.
 */
export default function Page() {
  return (
    <ScreenPad>
      <StickyHeader
        eyebrow="An sao · lập lá số"
        title="Chạm vào bầu trời ngày bạn sinh ra"
        subtitle="Xoay các vòng sao để nhập ngày sinh — chòm sao mệnh của bạn sẽ dần hiện lên."
      />

      <PrimitivesDemo />
      <ApiDemo />
      <ChartLockDemo />
      <AccentDemo />
    </ScreenPad>
  );
}
