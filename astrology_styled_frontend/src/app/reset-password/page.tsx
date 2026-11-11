import type { Metadata } from "next";

import { ResetPasswordScreen } from "@/features/auth/password-reset";

export const metadata: Metadata = {
  title: "Đặt lại mật khẩu · Thiên Hạc",
  description: "Chọn mật khẩu mới cho tài khoản Thiên Hạc.",
};

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { token, error } = await searchParams;

  return <ResetPasswordScreen token={typeof token === "string" && !error ? token : null} />;
}
