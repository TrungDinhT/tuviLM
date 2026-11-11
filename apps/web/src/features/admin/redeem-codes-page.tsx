import { notFound, redirect } from "next/navigation";

import { ScreenPad } from "@/components/shell/app-shell";
import { StickyHeader } from "@/components/shell/sticky-header";
import { getServerSession } from "@/lib/server-session";

import { RedeemCodesScreen } from "./redeem-codes-screen";

export async function RedeemCodesPage() {
  const session = await getServerSession();
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
