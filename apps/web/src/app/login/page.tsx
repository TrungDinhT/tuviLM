import type { Metadata } from "next";

import { AuthScreen } from "@/features/auth/auth-screen";

export const metadata: Metadata = {
  title: "Đăng nhập · Thiên Hạc",
  description: "Đăng nhập để tiếp tục hành trình luận giải lá số của bạn.",
};

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { error } = await searchParams;

  return <AuthScreen mode="login" callbackError={typeof error === "string" ? error : undefined} />;
}
