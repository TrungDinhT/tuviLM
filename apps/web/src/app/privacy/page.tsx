import type { Metadata } from "next";

import { PrivacyPolicy } from "@/features/legal/privacy-policy";

export const metadata: Metadata = {
  title: "Chính sách riêng tư · Thiên Hạc",
  description: "Thiên Hạc thu thập, sử dụng và bảo vệ dữ liệu của bạn như thế nào.",
};

export default function Page() {
  return <PrivacyPolicy />;
}
