import type { NextConfig } from "next";

import { env } from "./src/config/env";

const nextConfig: NextConfig = {
  devIndicators: false,

  /**
   * The `/api` rewrite below gives up after 30 s by default and answers 500,
   * while FastAPI finishes the request and spends the coins. The capability
   * report can take longer than that. Applies to `next dev` and `next start`.
   */
  experimental: { proxyTimeout: 120_000 },

  /**
   * Dev only. Next blocks cross-origin requests to dev assets, and the dev
   * server considers itself to be `localhost` — so opening it from a phone on
   * the same network serves the HTML but answers every `/_next/static/chunks/*`
   * request with 403. The page renders and nothing is interactive, because it
   * never hydrates.
   *
   * These are private LAN ranges, so the guard still holds against anything
   * off the local network. Has no effect on a production build.
   */
  allowedDevOrigins: ["192.168.*.*", "10.*.*.*", "172.16.*.*", "*.local"],

  /**
   * The browser calls `/api/*` on this site; Next forwards it to FastAPI.
   * Same origin means the login cookie is first-party, with no CORS. Works the
   * same in `next dev` and on Vercel.
   */
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${env.API_ORIGIN.replace(/\/$/, "")}/api/:path*`,
      },
    ];
  },

  /**
   * `public/` is served with `max-age=0`, so the loading crane the An sao
   * route prefetches would be revalidated — and re-sent in full — the moment
   * the loader plays it, which defeats the prefetch. An hour is long enough
   * to cover a session and short enough that a replaced asset still lands.
   */
  async headers() {
    return [
      {
        source: "/assets/:path*",
        headers: [{ key: "Cache-Control", value: "public, max-age=3600" }],
      },
    ];
  },
};

export default nextConfig;
