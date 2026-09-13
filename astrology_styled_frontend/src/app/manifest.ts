import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Thiên Hạc",
    short_name: "Thiên Hạc",
    description: "Thiên Hạc — lá số và luận giải Tử Vi",
    start_url: "/",
    display: "standalone",
    background_color: "#120A24",
    theme_color: "#1A1033",
    icons: [
      {
        src: "/assets/icons/android-chrome-192x192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/assets/icons/android-chrome-512x512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/assets/icons/maskable-icon-512x512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
