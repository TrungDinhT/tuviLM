import { Be_Vietnam_Pro, Fraunces } from "next/font/google";

/**
 * Display family. Fraunces is a variable font, so no `weight` is declared —
 * the whole 100..900 range ships. `opsz` is requested explicitly because the
 * design leans on optical sizing between 24px pickers and 38px palace titles.
 */
export const fraunces = Fraunces({
  subsets: ["latin", "vietnamese"],
  style: ["normal", "italic"],
  axes: ["opsz"],
  variable: "--font-fraunces",
  display: "swap",
});

/**
 * Body and UI family. Static weights, so every weight the design uses has to
 * be listed: 300 for long-form copy, 700 for eyebrows and locked-state labels.
 */
export const beVietnamPro = Be_Vietnam_Pro({
  subsets: ["latin", "vietnamese"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-be-vietnam-pro",
  display: "swap",
});
