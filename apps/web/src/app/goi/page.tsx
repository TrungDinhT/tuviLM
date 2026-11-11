import type { Metadata } from "next";

import { ScreenPad } from "@/components/shell/app-shell";
import { BalanceBadge } from "@/components/shell/balance-badge";
import { BrandLink } from "@/components/shell/brand-link";
import { PlansScreen } from "@/features/plans/plans-screen";

export const metadata: Metadata = { title: "Gói sử dụng · Thiên Hạc" };

export default function Page() {
  return (
    <ScreenPad>
      <header className="flex items-center justify-between gap-3 py-2 lg:hidden">
        <BrandLink />
        <BalanceBadge />
      </header>
      <PlansScreen />
    </ScreenPad>
  );
}
