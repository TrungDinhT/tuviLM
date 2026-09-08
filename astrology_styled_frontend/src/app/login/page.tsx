import type { Metadata } from "next";

import { AuthScreen } from "@/features/auth/auth-screen";

export const metadata: Metadata = {
  title: "Đăng nhập · Tử Vi",
  description: "Đăng nhập để tiếp tục hành trình luận giải lá số của bạn.",
};

export default function Page() {
  return <AuthScreen mode="login" />;
}
