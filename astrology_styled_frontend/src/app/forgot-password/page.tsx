import type { Metadata } from "next";

import { ForgotPasswordScreen } from "@/features/auth/password-reset";

export const metadata: Metadata = {
  title: "Quên mật khẩu · Thiên Hạc",
  description: "Nhận link đặt lại mật khẩu cho tài khoản Thiên Hạc.",
};

export default function Page() {
  return <ForgotPasswordScreen />;
}
