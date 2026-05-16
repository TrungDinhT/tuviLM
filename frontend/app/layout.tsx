import type { Metadata } from "next";
import { Lora, Be_Vietnam_Pro } from "next/font/google";
import "./globals.css";
import { Providers } from "./_components/Providers";

const lora = Lora({
  subsets: ["vietnamese", "latin"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  variable: "--font-lora",
  display: "swap",
});

const beVietnam = Be_Vietnam_Pro({
  subsets: ["vietnamese", "latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-be-vietnam",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Tuvi — Lập lá số, hỏi Thầy Tuệ",
  description: "An lá số Tử Vi theo phép cổ. Trò chuyện với Thầy Tuệ.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={`${lora.variable} ${beVietnam.variable}`}>
      <body className="paper-tex">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
