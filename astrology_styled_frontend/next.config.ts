import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,

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
};

export default nextConfig;
