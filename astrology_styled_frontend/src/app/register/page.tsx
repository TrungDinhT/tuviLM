import type { Metadata } from "next";

import { AuthScreen } from "@/features/auth/auth-screen";

export const metadata: Metadata = {
  title: "Đăng ký · Thiên Hạc",
  description: "Tạo tài khoản để lưu giữ hành trình luận giải lá số của bạn.",
};

export default function Page() {
  return <AuthScreen mode="register" />;
}
