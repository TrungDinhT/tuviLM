import { headers } from "next/headers";
import { notFound, redirect } from "next/navigation";

import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";
import { auth } from "@/lib/auth";

import { RedeemCodesScreen } from "./redeem-codes-screen";

export async function RedeemCodesPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
    query: { disableCookieCache: true },
  });
  if (!session) redirect("/login");
  if (session.user.role !== "admin") notFound();

  return (
    <ScreenPad>
      <StickyHeader
        eyebrow="Quản trị"
        title="Tạo mã nhận xu"
        subtitle="Chọn số xu, loại mã và thời hạn sử dụng."
      />
      <RedeemCodesScreen />
    </ScreenPad>
  );
}
