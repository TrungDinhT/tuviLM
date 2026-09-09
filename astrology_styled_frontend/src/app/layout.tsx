import type { Metadata, Viewport } from "next";

import { AccentTheme } from "@/components/providers/accent-theme";
import { QueryProvider } from "@/components/providers/query-provider";
import { StoreHydration } from "@/components/providers/store-hydration";
import { Toast } from "@/components/primitives/toast";
import { AppShell } from "@/components/shell/app-shell";
import { ColumnSky } from "@/components/shell/column-sky";
import { Cosmos } from "@/components/shell/cosmos";

import { beVietnamPro, fraunces } from "./fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tử Vi · An sao & luận giải",
  description: "An sao, đọc lá số và trò chuyện cùng Nghê Sao.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  // Required for env(safe-area-inset-*) to report anything but 0.
  viewportFit: "cover",
  colorScheme: "dark",
  // Tints the browser and Android navigation bars to match the shell. A meta
  // tag cannot read a CSS custom property, so this is a literal — keep it in
  // step with --color-bg-0.
  themeColor: "#1A1033",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={`${fraunces.variable} ${beVietnamPro.variable}`}>
      <body>
        <StoreHydration />
        <Cosmos />
        <ColumnSky />
        <QueryProvider>
          <AccentTheme>
            <AppShell>{children}</AppShell>
          </AccentTheme>
        </QueryProvider>
        <Toast />
      </body>
    </html>
  );
}
